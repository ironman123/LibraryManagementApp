function toggleFlex()
{
    var checkbox = document.getElementById('btn-check-2-outlined');
    var leftPanel = document.getElementById('leftPanel');
    var toggleLabel = document.getElementById('toggleLabel');

    var favouriteLabel = document.getElementById('favouriteLabel');
    var panelItemHeight = (favouriteLabel.clientHeight) / 2;

    var homeLabel = document.getElementById('homeLabel');
    var issuedLabel = document.getElementById('issuedLabel');
    var requestLabel = document.getElementById('requestLabel');
    //var bookLabel = document.getElementById('bookLabel');

    var genreLabel = document.getElementById('genreLabel'); 
    var authorLabel = document.getElementById('authorLabel');

    if (checkbox.checked)
    {
        leftPanel.style.flex = '1';
        toggleLabel.textContent = 'Menu';
        homeLabel.innerHTML = 'Home';
        favouriteLabel.innerHTML = 'Favourites';
        issuedLabel.innerHTML = 'Issued';
        requestLabel.innerHTML = 'Requests';
        //bookLabel.innerHTML = "Books"
        genreLabel.innerHTML = 'Genres';
        authorLabel.innerHTML = 'Authors';
    }
    else
    {
        leftPanel.style.flex = '0.3';
        toggleLabel.textContent = '≡';
        homeLabel.innerHTML = '<img src="../static/images/home.png" alt="Home Icon" height = "' + panelItemHeight + '">';
        favouriteLabel.innerHTML = '<img src="../static/images/favourite.png" alt="Heart Icon" height = "' + panelItemHeight + '">';
        issuedLabel.innerHTML = '<img src="../static/images/issued.png" alt="Book Icon" height = "' + panelItemHeight + '">';
        requestLabel.innerHTML = '<img src="../static/images/request.png" alt="Request Icon" height = "' + panelItemHeight + '">';
        //bookLabel.innerHTML = '<img src="../static/images/book.png" alt="Book Editor" height = "' + panelItemHeight + '">';
        genreLabel.innerHTML = '<img src="../static/images/genre.png" alt="Genre Editor" height = "' + panelItemHeight + '">';
        authorLabel.innerHTML = '<img src="../static/images/author.png" alt="Author Editor" height = "' + panelItemHeight + '">';
    }
}


function inputGenre(checkbox) 
{
    const inputField = document.getElementById('genre-input');
    const genre = checkbox.nextElementSibling.textContent.trim();
    
    if (checkbox.checked) 
    {
        const genres = inputField.value.split(',').map(genre => genre.trim().toLowerCase());
        
        if (!genres.includes(genre.toLowerCase()))
        {
            if (inputField.value === '')
            {
                inputField.value = genre;
            } 
            else 
            {
                inputField.value += ', ' + genre;
            }
        }
    }
    else 
    {
        inputField.value = inputField.value.replace(genre, '').replace(/(^,|,,| ,|, $)/g, '').trim();
    }
}


