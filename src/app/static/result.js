var flag = true;
var num = 1;
while(flag){
  var id = "caption" + num;
  if(num % 2 == 1 && num != 1){
    var current = document.getElementById(id);
    if(current == null){
      flag = false;
    }
    else{
      current.style.clear = "left";
    }
  }
  num = num + 1;
}
