// static/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    // Загрузка сохраненных параметров из localStorage
    document.getElementById('schemaName').value = localStorage.getItem('schemaName') || '{{ default_schemaName }}';
    document.getElementById('password').value = localStorage.getItem('password') || '{{ default_password }}';
    document.getElementById('serverName').value = localStorage.getItem('serverName') || '{{ default_serverName }}';
    document.getElementById('id_group_card').value = localStorage.getItem('id_group_card') || '{{ default_id_group_card }}';
    document.getElementById('AgreeType').value = localStorage.getItem('AgreeType') || '{{ default_AgreeType }}';

    // Обновление отображаемых параметров
    document.getElementById('displaySchemaName').innerText = localStorage.getItem('schemaName') || '{{ default_schemaName }}';
    document.getElementById('displayServerName').innerText = localStorage.getItem('serverName') || '{{ default_serverName }}';
    document.getElementById('displayIdGroupCard').innerText = localStorage.getItem('id_group_card') || '{{ default_id_group_card }}';
    document.getElementById('displayAgreeType').innerText = localStorage.getItem('AgreeType') || '{{ default_AgreeType }}';

    // Обновление скрытых полей в формах
    document.getElementById('schemaNameHidden').value = localStorage.getItem('schemaName') || '{{ default_schemaName }}';
    document.getElementById('passwordHidden').value = localStorage.getItem('password') || '{{ default_password }}';
    document.getElementById('serverNameHidden').value = localStorage.getItem('serverName') || '{{ default_serverName }}';
    document.getElementById('id_group_card_hidden').value = localStorage.getItem('id_group_card') || '{{ default_id_group_card }}';
    document.getElementById('AgreeType_hidden').value = localStorage.getItem('AgreeType') || '{{ default_AgreeType }}';
});

function updateConfig() {
    // Сохранение параметров в localStorage
    var schemaName = document.getElementById('schemaName').value;
    var password = document.getElementById('password').value;
    var serverName = document.getElementById('serverName').value;
    var id_group_card = document.getElementById('id_group_card').value;
    var AgreeType = document.getElementById('AgreeType').value;

    localStorage.setItem('schemaName', schemaName);
    localStorage.setItem('password', password);
    localStorage.setItem('serverName', serverName);
    localStorage.setItem('id_group_card', id_group_card);
    localStorage.setItem('AgreeType', AgreeType);

    // Обновление отображаемых параметров
    document.getElementById('displaySchemaName').innerText = schemaName;
    document.getElementById('displayServerName').innerText = serverName;
    document.getElementById('displayIdGroupCard').innerText = id_group_card;
    document.getElementById('displayAgreeType').innerText = AgreeType;

    // Обновление скрытых полей в формах
    document.getElementById('schemaNameHidden').value = schemaName;
    document.getElementById('passwordHidden').value = password;
    document.getElementById('serverNameHidden').value = serverName;
    document.getElementById('id_group_card_hidden').value = id_group_card;
    document.getElementById('AgreeType_hidden').value = AgreeType;

    // Логирование данных, отправляемых на сервер
    console.log(`Отправляемые данные: schemaName=${schemaName}, password=${password}, serverName=${serverName}, id_group_card=${id_group_card}, AgreeType=${AgreeType}`);

    // Отправка данных на сервер для логирования
    fetch('/update_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            schemaName: schemaName,
            password: password,
            serverName: serverName,
            id_group_card: id_group_card,
            AgreeType: AgreeType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Параметры подключения успешно обновлены на клиенте и сервере.');
        } else {
            alert('Ошибка при обновлении параметров на сервере.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function fillHiddenFields(event) {
    event.preventDefault();
    var schemaName = localStorage.getItem('schemaName') || document.getElementById('schemaName').value;
    var password = localStorage.getItem('password') || document.getElementById('password').value;
    var serverName = localStorage.getItem('serverName') || document.getElementById('serverName').value;

    document.getElementById('schemaNameHiddenAgreement').value = schemaName;
    document.getElementById('passwordHiddenAgreement').value = password;
    document.getElementById('serverNameHiddenAgreement').value = serverName;

    event.target.submit();
}
