// Auto-dismiss alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
      let bsAlert = new bootstrap.Alert(a);
      bsAlert.close();
    });
  }, 4000);
});