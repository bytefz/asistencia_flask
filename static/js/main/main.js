const div = document.querySelector("#table");
console.log(div);
div.addEventListener("scroll", () => {
    console.log(div.scrollTop)
    console.log(div.clientHeight)
    console.log(div.scrollHeight)
    if (div.scrollTop + div.clientHeight >= div.scrollHeight) loadMore();
});