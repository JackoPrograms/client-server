<template>
  <div class="teacher-student-view">
    <!-- Верхняя часть с поиском и кнопками -->
    <div class="header">
      <input type="text" v-model="search" placeholder="Поиск по имени..." class="search-bar" />
      <div class="buttons">
        <button @click="openModal" class="hire-button">
          {{ viewType === 'students' ? 'Зачислить' : 'Нанять' }}
        </button>
        <button @click="fireSelectedItems" class="fire-button">
          {{ viewType === 'students' ? 'Отчислить' : 'Уволить' }}
        </button>
      </div>
    </div>

    <!-- Таблица с данными -->
    <div class="table">
      <table>
        <thead>
          <tr>
            <th>Выбрать</th>
            <th>ФИО</th>
            <th>Кафедра</th>
            <th>Группа</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td colspan="5">Нет данных для отображения</td>
          </tr>
          <tr v-else v-for="item in filteredItems" :key="item.id">
            <td>
              <input type="checkbox" v-model="selectedItems" :value="item.id" />
            </td>
            <td>{{ item.name }}</td>
            <td>{{ item.department }}</td>
            <td>
              <!-- Отображаем группы для преподавателей или группу для студентов -->
              {{ viewType === 'teachers' ? item.groups?.join(', ') : item.group_name }}
            </td>
            <td>
              <button @click="openEditModal(item)">Подробнее</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модальное окно -->
    <div v-if="isModalOpen" class="modal-overlay">
      <div class="modal">
        <!-- Заголовок модального окна -->
        <h2>{{ viewType === 'teachers' ? 'Карточка преподавателя' : 'Карточка студента' }}</h2>
        <!-- Отображение изображения -->
        <img v-if="modalData.photo" :src="modalData.photo" alt="Фото пользователя" style="max-width: 100%; margin-bottom: 20px;" />
        <div class="modal-content">
          <!-- Остальные поля -->
        </div>
        <div class="modal-content">
          <label for="lastName">Фамилия</label>
          <input type="text" id="lastName" v-model="modalData.lastName" placeholder="Фамилия" />

          <label for="firstName">Имя</label>
          <input type="text" id="firstName" v-model="modalData.firstName" placeholder="Имя" />

          <label for="middleName">Отчество</label>
          <input type="text" id="middleName" v-model="modalData.middleName" placeholder="Отчество" />

          <label for="department">Кафедра</label>
          <select id="department" v-model="modalData.department">
            <option v-for="department in departments" :key="department" :value="department">{{ department }}</option>
          </select>

          <!-- Поле для даты рождения -->
          <label for="dateOfBirth">Дата рождения</label>
          <input type="date" id="dateOfBirth" v-model="modalData.dateOfBirth" />
        
          <!-- Поле для загрузки изображения -->
          <label for="photo">Фото</label>
          <input type="file" id="photo" @change="handleFileUpload" accept="image/*" />
        </div>
        <div class="modal-actions">
          <button @click="submitModal">Ок</button>
          <button @click="closeModal">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';

export default {
  props: {
    filter: {
      type: Object,
      required: true,
    },
    studentFilter: {
      type: Object,
      required: true,
    },
    viewType: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    // Проверка, что props переданы корректно
    if (!props || !props.viewType) {
        console.error('Props or viewType is undefined');
    }

    const socket = ref(null);
    const teachers = ref([]); // Данные преподавателей
    const students = ref([]); // Данные студентов
    const search = ref('');
    const selectedItems = ref([]); // Выбранные элементы
    const appliedFilter = ref(null); // Применённые фильтры
    const isModalOpen = ref(false); // Состояние модального окна
    const isNewRecord = ref(false); // Флаг для новой записи
    const modalData = ref({ // Данные для модального окна
      id: null,
      lastName: '',
      firstName: '',
      middleName: '',
      department: '',
      photo: '',
      dateOfBirth: '', // Добавлено поле для даты рождения
    });
    const departments = ref(['Кафедра 1', 'Кафедра 2', 'Кафедра 3']); // Список кафедр

    // Открытие модального окна для новой записи
    const openModal = () => {
      isNewRecord.value = true;
      modalData.value = {
        id: null,
        lastName: '',
        firstName: '',
        middleName: '',
        department: '',
        photo: '',
        dateOfBirth: '', // Сброс даты рождения
      };
      isModalOpen.value = true;
    };

    // Открытие модального окна для редактирования
    const openEditModal = (item) => {
      isNewRecord.value = false;
      const [lastName, firstName, middleName] = item.name.split(' ');
      modalData.value = {
        id: item.id,
        lastName,
        firstName,
        middleName,
        department: item.department,
        photo: item.photo,
        dateOfBirth: item.date_of_birth || '', // Устанавливаем дату рождения из данных
      };
      isModalOpen.value = true;
    };

    // Закрытие модального окна
    const closeModal = () => {
      isModalOpen.value = false;
      modalData.value = {
        id: null,
        lastName: '',
        firstName: '',
        middleName: '',
        department: '',
        photo: '',
        dateOfBirth: '', // Сброс даты рождения
      };
    };

    // Отправка данных из модального окна
    const submitModal = () => {
      if (!modalData.value.lastName || !modalData.value.firstName) {
        alert('Заполните фамилию и имя!');
        return;
      }

      const fullName = `${modalData.value.lastName} ${modalData.value.firstName} ${modalData.value.middleName || ''}`.trim();
      const data = {
        id: modalData.value.id,
        type: props.viewType === 'teachers' ? 'teacher' : 'student',
        name: fullName,
        department: modalData.value.department,
        photo: modalData.value.photo,
        dateOfBirth: modalData.value.dateOfBirth,
        action: isNewRecord.value ? 'create' : 'update',
      };

      console.log('Отправка данных на сервер:', data);  // Логируем данные перед отправкой

      const sendData = () => {
        if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
          console.log('Соединение закрыто. Пытаемся переподключиться...');
          socket.value = new WebSocket('ws://localhost:8000/ws');

          socket.value.onopen = () => {
            console.log('WebSocket соединение установлено');
            socket.value.send(JSON.stringify(data));  // Отправляем данные после переподключения
          };

          socket.value.onerror = (error) => {
            console.error('Ошибка WebSocket:', error);
            alert('Ошибка при подключении к WebSocket. Пожалуйста, перезагрузите страницу.');
          };

          socket.value.onclose = () => {
            console.log('WebSocket соединение закрыто');
          };
        } else {
          socket.value.send(JSON.stringify(data));  // Отправляем данные, если соединение открыто
        }
      };

      sendData();
      closeModal();  // Закрываем модальное окно после отправки
    };

    // Функция для увольнения/отчисления выбранных студентов или преподавателей
    const fireSelectedStudents = () => {
      if (selectedItems.value.length === 0) {
        alert('Выберите хотя бы одного!');
        return;
      }

      console.log('Выбранные элементы для удаления:', selectedItems.value); // Логирование выбранных элементов

      if (socket.value && socket.value.readyState === WebSocket.OPEN) {
        selectedItems.value.forEach(id => {
          const data = {
            id: id,
            action: 'fire', // Указываем действие "удалить"
            type: props.viewType === 'teachers' ? 'teacher' : 'student', // Указываем тип данных
          };

          console.log('Увольнение:', data); // Логирование для отладки
          console.log('Состояние WebSocket:', socket.value.readyState); // Логирование состояния WebSocket

          socket.value.send(JSON.stringify(data)); // Отправляем данные через WebSocket
        });

        // Очищаем список выбранных элементов
        selectedItems.value = [];
      } else {
        console.error('WebSocket соединение не установлено');
        alert('WebSocket соединение не установлено. Пожалуйста, перезагрузите страницу.');
      }
    };

    // Применение фильтров для преподавателей
    const applyFilter = (filter) => {
      appliedFilter.value = filter;
      console.log('Применён фильтр:', filter);
    };

    // Применение фильтров для студентов
    const applyStudentFilter = (studentFilter) => {
      appliedFilter.value = studentFilter;
      console.log('Применён фильтр для студентов:', studentFilter);
    };

    onMounted(() => {
      // Подключение к WebSocket серверу
      socket.value = new WebSocket('ws://localhost:8000/ws');

      // Обработка открытия соединения
      socket.value.onopen = () => {
        console.log('WebSocket соединение установлено');
      };

      // Обработка ошибок
      socket.value.onerror = (error) => {
        console.error('Ошибка WebSocket:', error);
      };

      // Получение сообщений от сервера
      socket.value.onmessage = (event) => {
        try {
            const parsedData = JSON.parse(event.data);
            console.log('Получены данные:', parsedData);

            // Обработка специальных сообщений
            if (parsedData.message === 'teacher_fired') {
                alert('Преподаватель успешно уволен. Группы перераспределены.');
            } else if (parsedData.message === 'student_expelled') {
                alert('Студент успешно отчислен.');
            }

            // Логируем данные о группах
            console.log('Группы преподавателей:', parsedData.teachers.map(t => t.groups));
            console.log('Группы студентов:', parsedData.students.map(s => s.group_name));

            // Обновляем данные
            teachers.value = parsedData.teachers || [];
            students.value = parsedData.students || [];
        } catch (error) {
            console.error('Ошибка обработки данных:', error);
        }
      };

      // Обработка закрытия соединения
      socket.value.onclose = () => {
        console.log('WebSocket соединение закрыто');
      };
    });

    onUnmounted(() => {
      if (socket.value) {
        socket.value.close();
      }
    });

    // Фильтрация данных на основе поиска и фильтров
    const filteredItems = computed(() => {
    if (!props || !props.viewType) {
        console.error('Props or viewType is undefined');
        return [];
    }

    const items = props.viewType === 'teachers' ? teachers.value : students.value;
      return items.filter(item => {
        const matchesSearch = item.name.toLowerCase().includes(search.value.toLowerCase());
        const matchesFilter = appliedFilter.value
          ? (!appliedFilter.value.department || item.department === appliedFilter.value.department) &&
            (!appliedFilter.value.group || 
              (props.viewType === 'teachers' 
                ? item.groups?.includes(appliedFilter.value.group)  // Для преподавателей
                : item.group_name === appliedFilter.value.group)) &&  // Для студентов
            (!appliedFilter.value.firstName || item.name.toLowerCase().includes(appliedFilter.value.firstName.toLowerCase())) &&
            (!appliedFilter.value.lastName || item.name.toLowerCase().includes(appliedFilter.value.lastName.toLowerCase())) &&
            (!appliedFilter.value.middleName || item.name.toLowerCase().includes(appliedFilter.value.middleName.toLowerCase()))
          : true;
        return matchesSearch && matchesFilter;
      });
    });

    const handleFileUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          modalData.value.photo = e.target.result; // Сохраняем изображение в формате Base64
        };
        reader.readAsDataURL(file); // Читаем файл как Data URL
      }
    };

    const fireSelectedItems = () => {
      if (selectedItems.value.length === 0) {
        alert(`Выберите хотя бы одного ${props.viewType === 'students' ? 'студента' : 'преподавателя'}!`);
        return;
      }

      if (socket.value && socket.value.readyState === WebSocket.OPEN) {
        selectedItems.value.forEach(id => {
          const data = {
            id: id,
            action: 'fire', // Указываем действие "удалить"
            type: props.viewType === 'students' ? 'student' : 'teacher', // Указываем тип данных
          };

          console.log(`Удаление ${props.viewType === 'students' ? 'студента' : 'преподавателя'}:`, data);
          socket.value.send(JSON.stringify(data)); // Отправляем данные через WebSocket
        });

        // Очищаем список выбранных элементов
        selectedItems.value = [];
      } else {
        console.error('WebSocket соединение не установлено');
        alert('WebSocket соединение не установлено. Пожалуйста, перезагрузите страницу.');
      }
    };

    return {
      search,
      teachers,
      students,
      filteredItems,
      selectedItems,
      isModalOpen,
      modalData,
      departments,
      openModal,
      openEditModal,
      closeModal,
      submitModal,
      fireSelectedStudents,
      applyFilter, // Возвращаем метод applyFilter
      applyStudentFilter, // Возвращаем метод applyStudentFilter
      handleFileUpload,
      fireSelectedItems,
    };
  },
};
</script>

<style scoped>
.teacher-student-view {
  margin-top: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-bar {
  padding: 8px;
  width: 60%;
  font-size: 16px;
}

.buttons {
  display: flex;
  gap: 10px;
}

.hire-button,
.fire-button {
  padding: 8px 12px;
  font-size: 14px;
}

.table {
  width: 100%;
  margin-top: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ccc;
}

th {
  background-color: #f4f4f4;
}

/* Стили для модального окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
}

.modal-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.modal h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}
</style>