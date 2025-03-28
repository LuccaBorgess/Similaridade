//variaveis
let loadingInterval;
let makingConsult = false;

//Varaiveis Principais
let selectedGenres;
let RateSelection;
let SelectedAuthor;
let SelectedTitle;
let PagesNum;
let SimilarsCount = 5;
let Classification;
let _Info;
let Books;

//Eventos
document.getElementById("Clear").addEventListener("click", function() {
    ClearAll();
});

document.getElementById("Consult").addEventListener("click", function() {
    makeConsult();
});

//Funções API
async function checkServerStatus() {
    try {
        const response = await fetch("http://127.0.0.1:5000", {
            method: "GET"
        });
        if (response.ok) {
            return true
        } else {
            return false
        }
    } catch (error) {
        return false
    }
}

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
        return data

    } catch (error) {
        console.error("Erro ao chamar o servidor:", error.message);
    }
}

async function GetBooks(_Info) {    
    try {
        const response = await fetch("http://127.0.0.1:5000/get_Books", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ _Info })
        });

        const data = await response.json();                
        return data

    } catch (error) {
        console.error("Erro ao chamar o servidor:", error.message);
    }
}

async function GetGenders() {           
    let checkedGenres = document.querySelectorAll(".container_genero input[type='checkbox']:checked");
    let Genres;

    Genres = Array.from(checkedGenres).map(checkbox => 
        checkbox.previousElementSibling.textContent.trim());
    
    if (Genres.length == 1){
        Genres = await getGenderKey(Genres);       
        Genres = Array.from(Genres.key)
    }

    return Genres
}

//Funções
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function ClearAll(){
    document.getElementById("Selections_Forms").reset();
    document.getElementById("Books_Bar").style.display = "none";    
    document.getElementById("Books_border").style.display = "none";
    makingConsult = false;    
}

async function GetMainVars(){
    const bookData = {};    

    //Valores Padrão sempre que Iniciar //RESET
    RateSelection   = "0";
    PagesNum        = 0;
    SelectedAuthor  = "";
    SelectedTitle   = ""; 
    Classification  = 0 ;

    //Coleta os Valores informados
    selectedGenres = await GetGenders()    
    RateSelection  = document.getElementById('Rate_Selection').value //Idade Informada
    PagesNum       = document.getElementById('Pages_IPT').value //Paginas    
    SelectedAuthor = document.getElementById('Author_IPT').value // Autor    
    SelectedTitle  = document.getElementById('Title_IPT').value // Titulo    
    Classification = document.getElementById('Classification_IPT').value //Nota   

    //Atribui os Valores de Forma selecionada
    if (selectedGenres != 0)    bookData[1] = selectedGenres;
    if (RateSelection  != "0")  bookData[2] = RateSelection;
    if (PagesNum       != 0)    bookData[3] = PagesNum;
    if (SelectedAuthor != "")   bookData[4] = SelectedAuthor;
    if (SelectedTitle  != "")   bookData[5] = SelectedTitle;        

    return Object.keys(bookData).length > 0 ? bookData : null;
}

function FillBooks(){
    //Melhor Opção Primeiro    

    console.log('Iniciou Preenchimento de Interface')

    const bestSelection = Books.key[0]      
    const GenderList    = bestSelection['Genero'].split(',');
    document.getElementById("Best_Selection_IMG").src = bestSelection['Capa']
    document.getElementById("Rate").textContent       = bestSelection['Classificação Indicativa']
    document.getElementById("PagesNum").textContent   = bestSelection['Paginas']
    document.getElementById("Author").textContent     = bestSelection['Autor']
    document.getElementById("Title").textContent      = bestSelection['Titulo']
    document.getElementById("Genders").textContent    = (GenderList.length > 0) ? GenderList.join("\n") : "";    

    const similarsContainer = document.getElementById('Similars'); 
    const bookTemplate      = document.getElementById('bookTemplate'); 

    const FirstSimilarSelection = Books.key[1] 
    const GenderListSimilar    = FirstSimilarSelection['Genero'].split(',');
    document.getElementById("Best_Selection_IMG_S").src = FirstSimilarSelection['Capa']
    document.getElementById("Rate_S").textContent       = FirstSimilarSelection['Classificação Indicativa']
    document.getElementById("PagesNum_S").textContent   = FirstSimilarSelection['Paginas']
    document.getElementById("Author_S").textContent     = FirstSimilarSelection['Autor']
    document.getElementById("Title_S").textContent      = FirstSimilarSelection['Titulo']
    document.getElementById("Genders_S").textContent    = (GenderListSimilar.length > 0) ? GenderListSimilar.join("\n") : "";    

    Books.key.forEach(book => {    
        if(book != bestSelection && book != FirstSimilarSelection) 
        {
            const bookClone = bookTemplate.cloneNode(true);
            
            const GenderList = book['Genero'].split(',');
        
            const imgElement = bookClone.querySelector('.img_livro');
            imgElement.src = book['Capa'];
            
            bookClone.querySelector('.p_opcoes').textContent = book['Titulo'];
            const pElements = bookClone.querySelectorAll('.p_opcoes');
            pElements[1].textContent = book['Classificação Indicativa'];
            pElements[2].textContent = book['Autor'];
            pElements[3].textContent = (GenderList.length > 0) ? GenderList.join("\n") : "";
            pElements[4].textContent = book['Idade'];
            pElements[5].textContent = book['Paginas'];

            similarsContainer.appendChild(bookClone);
        }
    });
}

function UpdateInterface(_Control){
    document.getElementById("Best_Selection").style.visibility     = (!_Control) ? "hidden" : "visible";
    document.getElementById("Best_Selection_IMG").style.visibility = (!_Control) ? "hidden" : "visible";
    document.getElementById("Similars_H").style.visibility         = (!_Control) ? "hidden" : "visible";
    document.getElementById("Similars").style.visibility           = (!_Control) ? "hidden" : "visible";
}

async function makeConsult() {        
    let   dots     = "";
    let   HasBooks = false;
    const bestSelectionH = document.getElementById("Best_Selection_H");
    
    clearInterval(loadingInterval);
    
    if(await checkServerStatus() == false){
        document.getElementById("Books_Bar").style.display    = "block";
        document.getElementById("Books_border").style.display = "block";

        UpdateInterface(false);

        bestSelectionH.innerText = 'Erro no Servidor'
        return;
    }

    makingConsult = true; 

    loadingInterval = setInterval(() => {
        if (!makingConsult) {
            clearInterval(loadingInterval);
            return;
        }
        dots = dots.length < 3 ? dots + "." : "";
        bestSelectionH.innerText = `Buscando Livros${dots}`;
    }, 400); 

    document.getElementById("Books_Bar").style.display    = "block";
    document.getElementById("Books_border").style.display = "block";
    
    UpdateInterface(false);

    _Info = await GetMainVars();            

    if(_Info != null){
        Books = await GetBooks([(_Info && Object.keys(_Info).length > 1 ? 2 : 1), _Info,SimilarsCount])
        console.log(Books)
        if(Books.key != 0){                       
            HasBooks = true
            FillBooks();
            bestSelectionH.innerText = "Melhor Opção";
        }
        else
            bestSelectionH.innerText = "Nenhum Livro Localizado"
    }
    else{ 
        clearInterval(loadingInterval);               
        bestSelectionH.innerText = "Nenhum Dado Informado"
    }   
    
    makingConsult = false

    if(HasBooks)
    {         
        clearInterval(loadingInterval);
        await sleep(500)        
        UpdateInterface(true);
    }
}