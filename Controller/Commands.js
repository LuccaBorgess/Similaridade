//variaveis
let loadingInterval;
let makingConsult = false;

//Varaiveis Principais
let selectedGenres;
let RateSelection;
let SelectedAuthor;
let SelectedTitle;
let PagesNum;
let SimilarsCount;

//Eventos
document.getElementById("Clear").addEventListener("click", function() {
    ClearAll();
});

document.getElementById("Consult").addEventListener("click", function() {
    makeConsult();
});

//Funções API
async function getGenderKey(genre) {
    try {
        const response = await fetch("http://127.0.0.1:5000/get_gender_key", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ genre })
        });

        const data = await response.json();        
        return data.key

    } catch (error) {
        console.error("Erro ao chamar o servidor:", error.message);
    }
}

//Funções
function ClearAll(){
    document.getElementById("Selections_Forms").reset();
    document.getElementById("Books_Bar").style.display = "none";    
    document.getElementById("Books_border").style.display = "none";
    makingConsult = false;
}

async function GetGenders() {   
    let checkedGenres = document.querySelectorAll(".container_genero input[type='checkbox']:checked");
    
    selectedGenres = Array.from(checkedGenres).map(checkbox => 
        checkbox.previousElementSibling.textContent.trim());
        
    if (selectedGenres.length == 1)
        selectedGenres = await getGenderKey(selectedGenres);            
    
    document.getElementById("Genders").textContent = (selectedGenres.length > 0) 
                                                    ? selectedGenres[0] : "";
}

function GetMainVars(){
    GetGenders();

    RateSelection = document.getElementById('Rate_Selection').value //Idade Informada
    document.getElementById("Rate").textContent = RateSelection

    PagesNum = document.getElementById('Pages_IPT').value //Paginas
    document.getElementById("PagesNum").textContent = PagesNum

    SelectedAuthor = document.getElementById('Author_IPT').value // Autor
    document.getElementById("Author").textContent = SelectedAuthor

    SelectedTitle = document.getElementById('Title_IPT').value // Titulo
    document.getElementById("Title").textContent = SelectedTitle

    SimilarsCount = document.getElementById('SimilarNum_IPT').value //Contagem de Similares
}

function makeConsult() {    
    const bestSelectionH = document.getElementById("Best_Selection_H");
    let dots = "";
    makingConsult = true; 
    clearInterval(loadingInterval);
        
    loadingInterval = setInterval(() => {
        if (!makingConsult) {
            clearInterval(loadingInterval);
            return;
        }
        dots = dots.length < 3 ? dots + "." : "";
        bestSelectionH.innerText = `Buscando Livros${dots}`;
    }, 600); 

    document.getElementById("Books_Bar").style.display = "block";
    document.getElementById("Books_border").style.display= "block";

    /*document.getElementById("Best_Selection").style.visibility = "hidden";
    document.getElementById("Best_Selection_IMG").style.visibility = "hidden";
    document.getElementById("Similars_H").style.visibility = "hidden";
    document.getElementById("Similars").style.visibility = "hidden";*/
    
    GetMainVars();

    //Faz a consulta

    //apos a consulta makingConsult = false

    /*document.getElementById("Best_Selection_H").innerText = 'Melhor Opção';
    document.getElementById("Best_Selection").style.visibility = "visible";
    document.getElementById("Best_Selection_IMG").style.visibility = "visible";

    document.getElementById("Similars_H").style.visibility = "visible";
    document.getElementById("Similars").style.visibility = "visible";*/
}