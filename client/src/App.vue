<template>
  <div id="app" class="app-container">
    <!-- Боковое меню -->
    <Sidebar
      v-model:filter="filter"
      v-model:studentFilter="studentFilter"
      @apply-filter="handleApplyFilter"
      @apply-student-filter="handleApplyStudentFilter"
      @switch-view="handleSwitchView"
      class="sidebar"
    />

    <!-- Основная часть -->
    <div class="main-content">
      <!-- Подключаем WebSocketService -->
      <WebSocketService
        ref="webSocketService"
        :filter="filter"
        :studentFilter="studentFilter"
        :viewType="selectedView"
      />
    </div>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue';
import WebSocketService from './components/WebSocketService.vue';

export default {
  components: {
    Sidebar,
    WebSocketService,
  },
  data() {
    return {
      filter: {
        department: '',
        group: '',
        firstName: '',
        lastName: '',
        middleName: '',
      },
      studentFilter: {
        department: '',
        group: '',
        firstName: '',
        lastName: '',
        middleName: '',
      },
      selectedView: 'teachers', // По умолчанию отображаем преподавателей
    };
  },
  methods: {
    handleApplyFilter(filter) {
      // Передаём фильтры для преподавателей в WebSocketService
      this.$refs.webSocketService.applyFilter(filter);
    },
    handleApplyStudentFilter(studentFilter) {
      // Передаём фильтры для студентов в WebSocketService
      this.$refs.webSocketService.applyStudentFilter(studentFilter);
    },
    handleSwitchView(view) {
      this.selectedView = view; // Обновляем выбранный вид
    },
  },
};
</script>

<style>
/* Контейнер для бокового меню и основной части */
.app-container {
  display: flex;
  min-height: 100vh; /* чтобы контейнер заполнил всю высоту */
}

/* Стили для бокового меню */
.sidebar {
  width: 250px;
  background-color: #f4f4f4;
  padding: 20px;
  box-sizing: border-box;
}

/* Стили для основной части */
.main-content {
  flex-grow: 1; /* основной контент занимает оставшееся место */
  padding: 20px;
}
</style>