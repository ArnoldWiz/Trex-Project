
document.addEventListener('DOMContentLoaded', () => {

    // =======================
    // CSRF TOKEN
    // =======================
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }
    const CSRF_TOKEN = getCSRFToken();

    const headersModificacion = {
        'Content-Type': 'application/json',
        'X-CSRFToken': CSRF_TOKEN 
    };

    // =======================
    // DOM ELEMENTS
    // =======================
    const listaComentarios = document.getElementById('lista-comentarios');
    const formComentario = document.getElementById('form-comentario');
    const btnConsultar = document.getElementById('btn-consultar');
    const btnDependiente = document.getElementById('btn-dependiente');
    const btnSubmitComentario = document.getElementById('btn-submit-comentario');
    const btnResetForm = document.getElementById('btn-reset-form');

    const inputId = document.getElementById('comentario-id');
    const inputMaquina = document.getElementById('comentario-maquina');
    const inputEmpleado = document.getElementById('comentario-empleado');
    const inputTexto = document.getElementById('comentario-texto');

    // =======================
    // HELPERS
    // =======================
    function renderComentarios(comentarios) {
        if (!listaComentarios) {
            console.warn('renderComentarios: no existe el elemento #lista-comentarios en esta página');
            return;
        }
        listaComentarios.innerHTML = '';
        comentarios.forEach(com => {
            const li = document.createElement('li');
            li.className = com.solucionado ? 'solucionado' : '';
            li.setAttribute('data-id', com.idcomentariosmaquinas);
            li.innerHTML = `
                <div class="info">
                    <strong>[ID: ${com.idcomentariosmaquinas}]</strong> 
                    (Máquina: ${com.maquina?.numero ?? 'Desconocida'}, 
                     Empleado: ${com.empleado?.nombre ?? 'Desconocido'} ${com.empleado?.apellidos ?? ''})
                    <p>${com.comentario}</p>
                    <small>Solucionado: ${com.solucionado ? 'Sí' : 'No'}</small>
                </div>
                <div class="acciones">
                    <button class="btn-solucionar" data-id="${com.idcomentariosmaquinas}">
                        Marcar como ${com.solucionado ? 'Pendiente' : 'Solucionado'} (PATCH)
                    </button>
                    <button class="btn-editar" data-id="${com.idcomentariosmaquinas}">Editar (Carga en form)</button>
                    <button class="btn-eliminar" data-id="${com.idcomentariosmaquinas}">Eliminar (DELETE)</button>
                </div>
            `;
            listaComentarios.appendChild(li);
        });
    }

    function resetForm() {
        if (inputId) inputId.value = '';
        if (inputMaquina) inputMaquina.value = '';
        if (inputEmpleado) inputEmpleado.value = '';
        if (inputTexto) inputTexto.value = '';
        if (btnSubmitComentario) {
            btnSubmitComentario.textContent = 'Crear Comentario (POST)';
            btnSubmitComentario.style.backgroundColor = '#28a745';
        }
        if (formComentario) formComentario.style.display = 'none';
    }

    // =======================
    // FETCH FUNCTIONS
    // =======================
    function consultarComentariosConThen() {
        fetch(API_URL)
            .then(res => res.ok ? res.json() : Promise.reject(res))
            .then(data => renderComentarios(data))
            .catch(err => console.error('GET error:', err));
    }

    function crearComentarioConThen(datos) {
        fetch(API_URL, {
            method: 'POST',
            headers: headersModificacion,
            body: JSON.stringify(datos)
        })
        .then(res => res.ok ? res.json() : res.json().then(err => Promise.reject(err)))
        .then(data => {
            alert(`¡Comentario ID ${data.idcomentariosmaquinas} creado!`);
            resetForm();
            if (listaComentarios) consultarComentariosConThen();
        })
        .catch(err => console.error('POST error:', err));
    }

    const modificarComentarioConAsync = async (id, datos) => {
        try {
            const res = await fetch(`${API_URL}${id}/`, {
                method: 'PUT',
                headers: headersModificacion,
                body: JSON.stringify(datos)
            });
            if (!res.ok) throw await res.json();
            const data = await res.json();
            alert(`Comentario ID ${data.idcomentariosmaquinas} modificado`);
            resetForm();
            if (listaComentarios) consultarComentariosConThen();
        } catch(err) { console.error('PUT error:', err); }
    };

    const toggleSolucionadoConAsync = async (id, estadoActual) => {
        try {
            const res = await fetch(`${API_URL}${id}/`, {
                method: 'PATCH',
                headers: headersModificacion,
                body: JSON.stringify({ solucionado: estadoActual ? 0 : 1 })
            });
            if (!res.ok) throw await res.json();
            await res.json();
            if (listaComentarios) consultarComentariosConThen();
        } catch(err) { console.error('PATCH error:', err); }
    };

    const eliminarComentarioConAsync = async (id) => {
        if (!confirm(`¿Eliminar comentario ${id}?`)) return;
        try {
            const res = await fetch(`${API_URL}${id}/`, {
                method: 'DELETE',
                headers: headersModificacion
            });
            if (res.status === 204) {
                if (listaComentarios) consultarComentariosConThen();
            } else throw await res.json();
        } catch(err) { console.error('DELETE error:', err); }
    };

    const crearYMarcarSolucionado = async () => {
        try {
            const datosComentario = {
                maquina_id: 1,
                empleado_id: 1,
                comentario: 'PETICIÓN DEPENDIENTE: Reporte automático',
                fecharegistro: new Date().toISOString(),
                solucionado: 0
            };
            const resCrear = await fetch(API_URL, {
                method: 'POST',
                headers: headersModificacion,
                body: JSON.stringify(datosComentario)
            });
            if (!resCrear.ok) throw await resCrear.json();
            const comentarioCreado = await resCrear.json();

            await fetch(`${API_URL}${comentarioCreado.idcomentariosmaquinas}/`, {
                method: 'PATCH',
                headers: headersModificacion,
                body: JSON.stringify({ solucionado: 1 })
            });

            if (listaComentarios) consultarComentariosConThen();
        } catch(err) { console.error('Dependiente error:', err); }
    };

    // =======================
    // EVENT LISTENERS
    // =======================
    if (btnConsultar) btnConsultar.addEventListener('click', consultarComentariosConThen);
    if (btnDependiente) btnDependiente.addEventListener('click', crearYMarcarSolucionado);
    if (btnResetForm) btnResetForm.addEventListener('click', resetForm);
    // Form visibility is controlled only when loading an item for edit; no manual show button.

    // Si la página define `CREATE_ON_PAGE`, dejamos que sea la propia página la que gestione
    // el envío (POST). En caso contrario, `reportes.js` se encarga del submit (crear/modificar).
    if (formComentario && !window.CREATE_ON_PAGE) formComentario.addEventListener('submit', e => {
        e.preventDefault();
        const id = inputId ? inputId.value : '';
        const datos = {
            maquina_id: inputMaquina ? inputMaquina.value : null,
            empleado_id: inputEmpleado ? inputEmpleado.value : null,
            comentario: inputTexto ? inputTexto.value : '',
            fecharegistro: new Date().toISOString(),
            solucionado: 0
        };
        if (id) modificarComentarioConAsync(id, datos);
        else crearComentarioConThen(datos);
    });

    if (listaComentarios) listaComentarios.addEventListener('click', async e => {
        const id = e.target.dataset.id;
        if (!id) return;

        if (e.target.classList.contains('btn-eliminar')) eliminarComentarioConAsync(id);
        if (e.target.classList.contains('btn-solucionar')) {
            const li = e.target.closest('li');
            toggleSolucionadoConAsync(id, li.classList.contains('solucionado'));
        }
        // Al hacer clic en EDITAR
if (e.target.classList.contains('btn-editar')) {
    try {
        const res = await fetch(`${API_URL}${id}/`);
        if (!res.ok) throw new Error('No se pudo cargar el comentario');
        const data = await res.json();

        if (inputId) inputId.value = data.idcomentariosmaquinas;
        if (inputMaquina) inputMaquina.value = data.maquina?.idmaquina ?? '';
        if (inputEmpleado) inputEmpleado.value = data.empleado?.idempleado ?? '';
        if (inputTexto) inputTexto.value = data.comentario;

        if (btnSubmitComentario) {
            btnSubmitComentario.textContent = `Modificar Comentario ${data.idcomentariosmaquinas}`;
            btnSubmitComentario.style.backgroundColor = '#007bff';
        }

        // 🔥 AQUÍ SE MUESTRA EL FORM Y SOLO AQUÍ 🔥
        if (formComentario) {
            formComentario.style.display = 'block';
            formComentario.scrollIntoView({ behavior: 'smooth' });
        }

    } catch(err) {
        alert(err.message);
    }
}

    });

    // Carga inicial (solo si hay lista o si existe botón de consulta)
    if (listaComentarios || btnConsultar) consultarComentariosConThen();
});
