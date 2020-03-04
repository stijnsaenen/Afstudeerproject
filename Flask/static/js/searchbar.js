const search = document.getElementById('search');
const matchList = document.getElementById('match-list');
const searchOption = document.getElementById('dropdownMenu5');


var searchOptionName = true;
var searchOptionEmail = false;
var searchOptionPhone = false;
var searchOptionCompanyName = false;


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
    var hihi = [{
        "contactId": id
    }];


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
            "name": persons[key].name,
            "email": persons[key].email,
            "phone": persons[key].phone,
            "companyname": persons[key].companyname
        };
        juisteLijstMetAlleNamenEnIds.push(pJson)
    })

    //matches met de input van search 
    let matches = juisteLijstMetAlleNamenEnIds.filter(person => {
        const regex = new RegExp(`^${searchText}`, 'gi');

        if (searchOptionName) {
            if (person.name == null) {
                console.log("error")
            } else if (person.name.match(regex)) {
                return person.name;
            }
        } else if (searchOptionEmail) {
            if (person.email == null) {
                console.log("error")
            } else if (person.email.match(regex)) {
                return person.email;
            }
        } else if (searchOptionPhone) {
            //TODO----------------------------------------------------------------------------------------------------------------------------------------------
            if (person.phone == null) {
                console.log("error")
            } else if (person.phone.match(regexnum)) {
                return person.name;
            }
        } else if (searchOptionCompanyName) {
            if (person.companyname == null) {
                console.log("error")
            } else if (person.companyname.match(regex)) {
                return person.name;
            }
        }
    });

    console.log(matches); //debug

    if (searchText.length === 0 || matches.length === 0) {
        matches = [];
        matchList.innerHTML = '';
    }

    if (search.value.length > 2) {
        outputHtml(matches);
    }
}

const outputHtml = matches => {
    if (matches.length > 0) {
        const html = matches.map(match => `

        <a class="list-group-item" onclick="
                                            sendIdToServer(${match.id});
                                            document.getElementById('search').value = '';
                                            document.getElementById('match-list').innerHTML = '';
                                            document.getElementById('displayrelatie').innerHTML = 'De relatie(s) van: <b>${match.name}</b>';

                                            ">${match.name}</a>
    
        `).join('');


        matchList.innerHTML = html;
    }

}
search.addEventListener('input', () => searchStates(search.value));






// verander opties van zoeken, veranderd gzn de booleans

nameoption = document.getElementById('nameoption');
mailoption = document.getElementById('mailoption');
cnameoption = document.getElementById('cnameoption');

function changeSearchOptionName() {
    nameoption.classList.add("active");
    mailoption.classList.remove("active");
    cnameoption.classList.remove("active");


    searchOption.innerHTML = 'Name';
    searchOptionName = true;
    searchOptionEmail = false;
    searchOptionPhone = false;
    searchOptionCompanyName = false;
    matches = [];
}

function changeSearchOptionEmail() {
    mailoption.classList.add("active");
    nameoption.classList.remove("active");
    cnameoption.classList.remove("active");

    searchOption.innerHTML = 'E-Mail';
    searchOptionName = false;
    searchOptionEmail = true;
    searchOptionPhone = false;
    searchOptionCompanyName = false;
    matches = [];
}

/* function changeSearchOptionPhone() {

    searchOptionName = false;
    searchOptionEmail = false;
    searchOptionPhone = true;
    searchOptionCompanyName = false;
    matches = [];
} */

function changeSearchOptionCompanyName() {
    nameoption.classList.remove("active");
    mailoption.classList.remove("active");
    cnameoption.classList.add("active");

    searchOption.innerHTML = 'Company name';
    searchOptionName = false;
    searchOptionEmail = false;
    searchOptionPhone = false;
    searchOptionCompanyName = true;
    matches = [];
}