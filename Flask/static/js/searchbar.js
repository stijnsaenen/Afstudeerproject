const search = document.getElementById('search');
const matchList = document.getElementById('match-list');

//search json en filter
const JSONlist = getJsonList();

function getJsonList() {
    var res = function () {
        var result = null;
        $.ajax({
            type: "GET",
            async: false,
            global: false,
            url: '/id',
            success: function (data) {
                result = data;
            },
            error: function (data) {
                console.log("nee");
            }
        });
        return result;
    }();
    return res;

}

function sendIdToServer(id) {
    console.log(id);
    var hihi = [{ "contactId": id }];

    $.ajax({
        type: "POST",
        url: '/receivePersonID',
        /* data: id, */
        data: JSON.stringify(hihi),
        contentType: "application/json",
        success: function (response) {
            createD3(response);
        },
        error: function (data) {
            console.log(data);
            console.log(JSON.stringify(hihi))
        }
    });
}

const searchStates = async searchText => {
    const persons = JSON.parse(JSONlist);

    const juisteLijstMetAlleNamenEnIds = [] //convert naar juiste format
    Object.keys(persons).forEach(function (key) {
        var pJson = {
            "id": persons[key].id,
            "name": persons[key].name
        };
        juisteLijstMetAlleNamenEnIds.push(pJson)
    })

    //matches met de input van search 
    let matches = juisteLijstMetAlleNamenEnIds.filter(person => {
        const regex = new RegExp(`^${searchText}`, 'gi');

        return person.name.match(regex);
    });

    //console.log(matches); //debug

    if (searchText.length === 0 || matches.length === 0) {
        matches = [];
        matchList.innerHTML = '';
    }

    if (search.value.length > 0) {
        outputHtml(matches);
    }
}

const outputHtml = matches => {
    if (matches.length > 0) {
        const html = matches.map(match => `

        <a class="dropdown-item" onclick="sendIdToServer(${match.id})">${match.name}</a>
    
        `).join('');


        matchList.innerHTML = html;
    }
}
search.addEventListener('input', () => searchStates(search.value));

