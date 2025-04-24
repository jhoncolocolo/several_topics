
```
<div id="mensajeServidor" class="alert alert-success" style="display: none;"></div>

 fetch('TU_URL_POST', {
  method: 'POST',
  // ... otras configuraciones como headers y body ...
})
.then(response => response.json())
.then(data => {
  const mensajeDiv = document.getElementById('mensajeServidor');

  if (data.satisfactorio) {
    mensajeDiv.textContent = data.body.mensajeDelServidor; // Asumiendo que el mensaje está en data.body.mensajeDelServidor
    mensajeDiv.style.display = 'block'; // Mostrar el mensaje
    // Opcional: Puedes ocultar el mensaje después de unos segundos
    setTimeout(() => {
      mensajeDiv.style.display = 'none';
    }, 5000); // Ocultar después de 5 segundos (5000 milisegundos)
  } else {
    // Opcional: Mostrar un mensaje de error si la respuesta no es satisfactoria
    mensajeDiv.className = 'alert alert-danger'; // Cambiar la clase a rojo
    mensajeDiv.textContent = 'Error: ' + (data.body.mensajeError || 'Hubo un problema con la solicitud.');
    mensajeDiv.style.display = 'block';
    setTimeout(() => {
      mensajeDiv.style.display = 'none';
      mensajeDiv.className = 'alert alert-success'; // Volver a la clase original para futuros mensajes
    }, 5000);
  }

  console.log(data); // Puedes dejar este console.log para depuración
})
.catch(error => {
  console.error('Error en la petición:', error);
  const mensajeDiv = document.getElementById('mensajeServidor');
  mensajeDiv.className = 'alert alert-danger';
  mensajeDiv.textContent = 'Error en la conexión con el servidor.';
  mensajeDiv.style.display = 'block';
  setTimeout(() => {
    mensajeDiv.style.display = 'none';
    mensajeDiv.className = 'alert alert-success'; // Volver a la clase original
  }, 5000);
});
```
