function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}


 function displayRadioValueAccountStatus(){
        var account_status = document.getElementById("account_status");
        var ele_accountStatus = document.getElementsByName("accountStatus");
        for (var i = 0; i < ele_accountStatus.length; i++) {
            if(ele_accountStatus[i].checked)
                account_status.setAttribute('value',ele_accountStatus[i].value);
         }
      }


 function displayRadioValueProjectStatus(){
        var project_status = document.getElementById("project_status");
        var ele_prjStatus = document.getElementsByName("prjStatus");
        for (var i = 0; i < ele_prjStatus.length; i++) {
            if(ele_prjStatus[i].checked)
                project_status.setAttribute('value',ele_prjStatus[i].value);
         }
      }


 function displayRadioValueUserRole(){
        var user_role = document.getElementById("user_role");
        var ele_userRole = document.getElementsByName("userRole");
        for (var i = 0; i < ele_userRole.length; i++) {
            if(ele_userRole[i].checked)
                user_role.setAttribute('value',ele_userRole[i].value);
         }
      }


 function displayRadioValueDeviceIsActive(){
        var device_status = document.getElementById("device_is_active");
        var ele_deviceStatus = document.getElementsByName("deviceIsActive");
        for (var i = 0; i < ele_deviceStatus.length; i++) {
            if(ele_deviceStatus[i].checked)
                device_status.setAttribute('value',ele_deviceStatus[i].value);
         }
      }


 function displayRadioValueDeviceStatus(){
        var device_status = document.getElementById("device_status");
        var ele_deviceStatus = document.getElementsByName("deviceStatus");
        for (var i = 0; i < ele_deviceStatus.length; i++) {
            if(ele_deviceStatus[i].checked)
                device_status.setAttribute('value',ele_deviceStatus[i].value);
         }
      }



 function displayRadioValueTcIsActive(){
        var tc_status = document.getElementById("tc_is_active");
        var ele_tcStatus = document.getElementsByName("tcIsActive");
        for (var i = 0; i < ele_tcStatus.length; i++) {
            if(ele_tcStatus[i].checked)
                tc_status.setAttribute('value',ele_tcStatus[i].value);
         }
      }


 function displayRadioValueCondIsActive(){
        var cond_status = document.getElementById("cond_is_active");
        var ele_condStatus = document.getElementsByName("condIsActive");
        for (var i = 0; i < ele_condStatus.length; i++) {
            if(ele_condStatus[i].checked)
                cond_status.setAttribute('value',ele_condStatus[i].value);
         }
      }


function searchStatus() {
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("searchStatus");
  filter = input.value.toUpperCase();
  table = document.getElementById("runningTable");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[3];
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
