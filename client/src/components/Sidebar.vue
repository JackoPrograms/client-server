<template>
  <div class="sidebar">
    <div class="menu">
      <!-- Кнопка "Преподаватели" -->
      <div class="menu-item">
        <button @click="switchView('teachers')" :class="{ active: selectedView === 'teachers' }">
          Преподаватели
        </button>
        <button class="filter-button" @click="toggleFilter('teachers')">
          <img src="https://avatars.mds.yandex.net/i?id=606fa449c1f1a3797ef7c1b790139582_l-5238336-images-thumbs&n=13" alt="filter" />
        </button>
      </div>

      <!-- Фильтры для преподавателей -->
      <div v-if="filtersVisible.teachers" class="filter-container">
        <div class="filters">
          <div class="filter">
            <label for="department">Кафедры</label>
            <select id="department" v-model="filter.department">
              <option v-for="department in departments" :key="department" :value="department">{{ department }}</option>
            </select>
          </div>
          <div class="filter">
            <label for="group">Группы</label>
            <select id="group" v-model="filter.group">
              <option v-for="group in groups" :key="group" :value="group">{{ group }}</option>
            </select>
          </div>
          <div class="filter">
            <label for="firstName">Имя</label>
            <input type="text" id="firstName" v-model="filter.firstName" placeholder="Имя" />
          </div>
          <div class="filter">
            <label for="lastName">Фамилия</label>
            <input type="text" id="lastName" v-model="filter.lastName" placeholder="Фамилия" />
          </div>
          <div class="filter">
            <label for="middleName">Отчество</label>
            <input type="text" id="middleName" v-model="filter.middleName" placeholder="Отчество" />
          </div>
          <button @click="applyFilter">Применить</button>
        </div>
      </div>

      <!-- Кнопка "Студенты" -->
      <div class="menu-item">
        <button @click="switchView('students')" :class="{ active: selectedView === 'students' }">
          Студенты
        </button>
        <button class="filter-button" @click="toggleFilter('students')">
          <img src="https://avatars.mds.yandex.net/i?id=606fa449c1f1a3797ef7c1b790139582_l-5238336-images-thumbs&n=13" alt="filter" />
        </button>
      </div>

      <!-- Фильтры для студентов -->
      <div v-if="filtersVisible.students" class="filter-container">
        <div class="filters">
          <div class="filter">
            <label for="studentDepartment">Кафедры</label>
            <select id="studentDepartment" v-model="studentFilter.department">
              <option v-for="department in departments" :key="department" :value="department">{{ department }}</option>
            </select>
          </div>
          <div class="filter">
            <label for="studentGroup">Группы</label>
            <select id="studentGroup" v-model="studentFilter.group">
              <option v-for="group in groups" :key="group" :value="group">{{ group }}</option>
            </select>
          </div>
          <div class="filter">
            <label for="studentFirstName">Имя</label>
            <input type="text" id="studentFirstName" v-model="studentFilter.firstName" placeholder="Имя" />
          </div>
          <div class="filter">
            <label for="studentLastName">Фамилия</label>
            <input type="text" id="studentLastName" v-model="studentFilter.lastName" placeholder="Фамилия" />
          </div>
          <div class="filter">
            <label for="studentMiddleName">Отчество</label>
            <input type="text" id="studentMiddleName" v-model="studentFilter.middleName" placeholder="Отчество" />
          </div>
          <button @click="applyStudentFilter">Применить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['update:filter', 'apply-filter', 'switch-view', 'update:student-filter', 'apply-student-filter'],
  props: {
    filter: {
      type: Object,
      required: true,
    },
    studentFilter: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      selectedView: 'teachers',
      filtersVisible: {
        teachers: false,
        students: false,
      },
      departments: ['Кафедра 1', 'Кафедра 2', 'Кафедра 3'],
      groups: ['Группа 1', 'Группа 2', 'Группа 3'],
    };
  },
  methods: {
    switchView(view) {
      this.selectedView = view;
      this.$emit('switch-view', view);

      // Сбрасываем фильтры для другой вкладки и сворачиваем её
      if (view === 'teachers') {
        this.studentFilter.department = '';
        this.studentFilter.group = '';
        this.studentFilter.firstName = '';
        this.studentFilter.lastName = '';
        this.studentFilter.middleName = '';
        this.filtersVisible.students = false; // Сворачиваем фильтры для студентов
      } else {
        this.filter.department = '';
        this.filter.group = '';
        this.filter.firstName = '';
        this.filter.lastName = '';
        this.filter.middleName = '';
        this.filtersVisible.teachers = false; // Сворачиваем фильтры для преподавателей
      }
    },
    toggleFilter(view) {
      // Переключаемся на соответствующую вкладку
      this.switchView(view);

      // Сворачиваем фильтры для другой вкладки
      if (view === 'teachers') {
        this.filtersVisible.students = false;
      } else {
        this.filtersVisible.teachers = false;
      }

      // Разворачиваем или сворачиваем фильтры для текущей вкладки
      this.filtersVisible[view] = !this.filtersVisible[view];
    },
    applyFilter() {
      this.$emit('apply-filter', this.filter);
    },
    applyStudentFilter() {
      this.$emit('apply-student-filter', this.studentFilter);
    },
  },
  watch: {
    filter: {
      handler(newFilter) {
        this.$emit('update:filter', newFilter);
      },
      deep: true,
    },
    studentFilter: {
      handler(newFilter) {
        this.$emit('update:student-filter', newFilter);
      },
      deep: true,
    },
  },
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu button {
  width: 100%;
  padding: 10px;
  height: 40px;
  background-color: #f0f0f0;
  color: black;
  border: 1px solid #3c3c3c;
  cursor: pointer;
  font-size: 16px;
  text-align: center;
}

.menu-item .filter-button {
  background-color: #f0f0f0;
  border: 1px solid #3c3c3c;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.menu-item .filter-button img {
  width: 20px;
  height: 20px;
}

.filter-container {
  margin-top: 20px;
}

.filters {
  display: flex;
  flex-direction: column;
}

.filter {
  margin-bottom: 10px;
  width: 100%;
}

label {
  display: block;
  margin-bottom: 5px;
}

select,
input[type="text"] {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

button {
  padding: 8px 15px;
  background-color: #f0f0f0;
  color: black;
  border: 1px solid #3c3c3c;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

button:hover {
  background-color: #c4c4c4;
}
</style>