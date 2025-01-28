document.addEventListener('DOMContentLoaded', function() {
    // Загрузка сохраненных параметров из localStorage или использование значений по умолчанию из ini
    document.getElementById('schemaName').value = localStorage.getItem('schemaName') || '{{ default_schemaName }}';
    document.getElementById('password').value = localStorage.getItem('password') || '{{ default_password }}';
    document.getElementById('serverName').value = localStorage.getItem('serverName') || '{{ default_serverName }}';
    document.getElementById('id_group_card').value = localStorage.getItem('id_group_card') || '{{ default_id_group_card }}';
    document.getElementById('AgreeType').value = localStorage.getItem('AgreeType') || '{{ default_AgreeType }}';

    // Обновление скрытых полей в формах
    updateHiddenFields();
});

function updateConfig(fromForm = false) {
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

    // Обновление скрытых полей в формах
    updateHiddenFields();

    if (!fromForm) {
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
}

function updateHiddenFields() {
    var schemaName = localStorage.getItem('schemaName') || document.getElementById('schemaName').value;
    var password = localStorage.getItem('password') || document.getElementById('password').value;
    var serverName = localStorage.getItem('serverName') || document.getElementById('serverName').value;
    var id_group_card = localStorage.getItem('id_group_card') || document.getElementById('id_group_card').value;
    var AgreeType = localStorage.getItem('AgreeType') || document.getElementById('AgreeType').value;

    document.getElementById('schemaNameHidden').value = schemaName;
    document.getElementById('passwordHidden').value = password;
    document.getElementById('serverNameHidden').value = serverName;
    document.getElementById('id_group_card_hidden_client').value = id_group_card;
    document.getElementById('AgreeType_hidden_client').value = AgreeType;
    document.getElementById('schemaNameHiddenAgreement').value = schemaName;
    document.getElementById('passwordHiddenAgreement').value = password;
    document.getElementById('serverNameHiddenAgreement').value = serverName;
    document.getElementById('id_group_card_hidden_agreement').value = id_group_card;
    document.getElementById('AgreeType_hidden_agreement').value = AgreeType;
}
