const sidebar = document.getElementById('sidebar');
    const filterButton = document.getElementById('filterButton');

    filterButton.addEventListener('click', function() {
      sidebar.classList.toggle('show');
      // Изменяем текст кнопки в зависимости от состояния сайдбара
      if (sidebar.classList.contains('show')) {
        filterButton.textContent = 'Скрыть фильтр';
      } else {
        filterButton.textContent = 'Показать фильтр';
      }
    });