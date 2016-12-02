function changeContent(str){
  var addon = '&nbsp;<span class="caret"></span>';
  document.getElementById("dropdownMenu1").innerHTML = str + addon;

  if (str.indexOf('All') == -1)
    document.getElementById("distance").value = str;
  else
    document.getElementById("distance").value = "";

}

function geolocate() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(updatePosition);
    }
    else {
        //should find a better way to do this
        alert('Geolocation not supported, should handle this');
    }
}

function changeCategory(category) {
    category_input = document.getElementById("category");
    old_category = category_input.value;
    category_input.value = category;
    old_selection = document.getElementById(old_category)
    if (old_selection && old_selection.className.indexOf(" active") != -1)
        old_selection.className = old_selection.className.replace(" active", "");
    if (old_selection && old_selection.id && old_selection.id != category)
        document.getElementById(category).className += " active";
    if (oldselection && old_selection.id && old_selection.id == category)
        category_input.value = ""



}

//should fix this, probably should use ajax call to google maps api to get address
//from position.latitude and postiition.longitude
function updatePosition(position) {
    var location_field = document.getElementById("location_field");
    var location_display = document.getElementById("location_display");
    //location_field.value = position;
    //location_display.innerHTML = position;
}
