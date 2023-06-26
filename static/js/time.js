const min = document.getElementById("min");
const sec = document.getElementById("sec");


function countdown() {
    if(time >= 0){
    var a_min = Math.floor(time/60);
    var a_sec = time % 60;

    time = time - 1;

    min.innerHTML = a_min < 10 ? '0' + a_min:a_min;
    sec.innerHTML = a_sec < 10 ? '0' + a_sec:a_sec;
    }else{

    }

}
countdown();
setInterval(countdown,1000);