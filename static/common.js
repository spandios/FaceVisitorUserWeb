
function swalErrorMessage(Swal,message){
    Swal.fire({
        text:message,
        icon:'error'
    })
}

function swalError(Swal, e) {
    console.log(e);
    if (e.response.status === 400) {
        Swal.fire({
            text: e.response.data,
            icon: 'error',
        });
    } else if(e.response.status === 404){
        Swal.fire({
            text: e.response.data.message,
            icon: 'error',
        });
    } else if (e.response.status === 401) {
        Swal.fire({
            text: "유저 정보를 찾을 수 없습니다. 다시 로그인 해주세요",
            icon: 'error',
        }).then(result => {
            return location.href = "/login";
        });
    } else {
        Swal.fire({
            text: "서버 에러가 있습니다.",
            icon: 'error',
        });
    }
}

