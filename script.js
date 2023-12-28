
for (let node of document.querySelectorAll('svg .node')) {

    node.addEventListener('click', evt => {
        node.classList.toggle('active')
    })
}