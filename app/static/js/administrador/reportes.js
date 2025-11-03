
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
        inputId.value = '';
        inputMaquina.value = '';
        inputEmpleado.value = '';
        inputTexto.value = '';
        btnSubmitComentario.textContent = 'Crear Comentario (POST)';
        btnSubmitComentario.style.backgroundColor = '#28a745';
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
            consultarComentariosConThen();
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
            consultarComentariosConThen();
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
            consultarComentariosConThen();
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
                consultarComentariosConThen();
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

            consultarComentariosConThen();
        } catch(err) { console.error('Dependiente error:', err); }
    };

    // =======================
    // EVENT LISTENERS
    // =======================
    btnConsultar.addEventListener('click', consultarComentariosConThen);
    btnDependiente.addEventListener('click', crearYMarcarSolucionado);
    btnResetForm.addEventListener('click', resetForm);

    formComentario.addEventListener('submit', e => {
        e.preventDefault();
        const id = inputId.value;
        const datos = {
            maquina_id: inputMaquina.value,
            empleado_id: inputEmpleado.value,
            comentario: inputTexto.value,
            fecharegistro: new Date().toISOString(),
            solucionado: 0
        };
        if (id) modificarComentarioConAsync(id, datos);
        else crearComentarioConThen(datos);
    });

    listaComentarios.addEventListener('click', async e => {
        const id = e.target.dataset.id;
        if (!id) return;

        if (e.target.classList.contains('btn-eliminar')) eliminarComentarioConAsync(id);
        if (e.target.classList.contains('btn-solucionar')) {
            const li = e.target.closest('li');
            toggleSolucionadoConAsync(id, li.classList.contains('solucionado'));
        }
        if (e.target.classList.contains('btn-editar')) {
            try {
                const res = await fetch(`${API_URL}${id}/`);
                if (!res.ok) throw new Error('No se pudo cargar el comentario');
                const data = await res.json();
                inputId.value = data.idcomentariosmaquinas;
                inputMaquina.value = data.maquina?.idmaquina ?? '';
                inputEmpleado.value = data.empleado?.idempleado ?? '';
                inputTexto.value = data.comentario;
                btnSubmitComentario.textContent = `Modificar Comentario ${data.idcomentariosmaquinas} (PUT)`;
                btnSubmitComentario.style.backgroundColor = '#007bff';
                formComentario.scrollIntoView({ behavior: 'smooth' });
            } catch(err) { alert(err.message); }
        }
    });

    // Carga inicial
    consultarComentariosConThen();
});
