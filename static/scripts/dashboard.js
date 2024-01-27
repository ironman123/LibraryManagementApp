function toggleFlex() {
    var checkbox = document.getElementById('btn-check-2-outlined');
    var leftPanel = document.getElementById('leftPanel');
    var toggleLabel = document.getElementById('toggleLabel');
    
    var favouriteLabel = document.getElementById('favouriteLabel');
    var panelItemHeight = (favouriteLabel.clientHeight)/1.5;

    var issuedLabel = document.getElementById('issuedLabel');
    var historyLabel = document.getElementById('historyLabel');

    if (checkbox.checked) {
        leftPanel.style.flex = '1';
        toggleLabel.textContent = 'Menu';
        favouriteLabel.innerHTML = 'Favourites';
        issuedLabel.innerHTML = 'Issued';
        historyLabel.innerHTML = 'History';
    } else {
        leftPanel.style.flex = '0.3';
        toggleLabel.textContent = '≡';
        favouriteLabel.innerHTML = '<img src="../static/images/favourite.png" alt="Heart Icon" height = "'+panelItemHeight+'">';
        issuedLabel.innerHTML = '<img src="../static/images/issued.png" alt="Book Icon" height = "'+panelItemHeight+'">';
        historyLabel.innerHTML = '<img src="../static/images/history.png" alt="History Icon" height = "'+panelItemHeight+'">';
    }
}