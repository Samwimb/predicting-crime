function myFunction() {
    // Declare variables 
    var td, i, txtValue;

    var input = d3.select("#myInput");
    var filter = input.value.toUpperCase();
    var table = d3.select("#myTable");
    var tr = d3.select("tr");
  
    // filtering: Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[0];
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      } 
    }
  }


