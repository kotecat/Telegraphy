function domToNode(domNode) {
    
    if (domNode.nodeType == domNode.TEXT_NODE) {
      return domNode.data.trim();
    }
    if (domNode.nodeType != domNode.ELEMENT_NODE) {
      return false;
    }
    if (domNode.tagName.toLowerCase() == 'span') {
      return domNode.textContent; 
    }
    var nodeElement = {};
    nodeElement.tag = domNode.tagName.toLowerCase();
    for (var i = 0; i < domNode.attributes.length; i++) {
      var attr = domNode.attributes[i];
      if (attr.name == 'href' || attr.name == 'src') {
        if (!nodeElement.attrs) {
          nodeElement.attrs = {};
        }
        nodeElement.attrs[attr.name] = attr.value;
      }
    }
    if (domNode.childNodes.length > 0) {
      nodeElement.children = [];
      for (var i = 0; i < domNode.childNodes.length; i++) {
        var child = domNode.childNodes[i];
        var childNode = domToNode(child);

        if (childNode instanceof Array) {
            nodeElement.children.push(...childNode)
        }
        else if (childNode !== "") {
            nodeElement.children.push(childNode);
        }
      }
    }
    return nodeElement;
}


(async () => {
    const account = await autoCreateAccount();
    
    if (window.location.pathname != "/") {
        const page = await getPageInfo();
        const edit = await isAllowEdit();
    
        const editBtn = document.getElementById("edit-html"); 
        editBtn.textContent = edit ? "Edit" : "Edit & Copy";
        editBtn.disabled = false;
    
        if (edit) {
            const deleteBtn = document.getElementById("delete-html"); 
            deleteBtn.style.display = "block";
            deleteBtn.disabled = false;
        }

        await addView(page.path);
        return;
    }

    const author = document.getElementById("author");
    author.innerText = account.author_name;
    author.href = account.author_url;

    document.getElementById("link-input").innerText = account.author_url || "...";

    prepareEditor();
    
})();


var Block = Quill.import('blots/block');
Block.tagName = "p";
Quill.register(Block);

var quills = {};


function initEditor() {
    quills.mainQuill = new Quill('#content_payload', {
        theme: 'snow',
        scrollingContainer: 'html',
        modules: {
            toolbar: {
                container: [
                    ['bold', 'italic', 'underline', "code"],
                    ['link', 'image', "blockquote"],
                    [{ list: 'ordered' }, { list: 'bullet' }],
                    [{ header: [1, 3, 4, false] }],
                    ['clean']
                ],
                handlers: {
                    image: function () {
                        const imageUrl = prompt('Image Link:');
                        if (imageUrl) {
                            const range = quills.mainQuill.getSelection();
                            quills.mainQuill.insertEmbed(range.index, 'image', imageUrl);
                        }
                    }
                }
            }
        }
    });

    document.getElementById("link-input-block").style.display = "block";
    document.getElementById("link-input").contentEditable = true;
    document.getElementById("title").contentEditable = true;
    document.getElementById("author").contentEditable = true;
}


function prepareEditor() {
    const editBtn = document.getElementById("edit-html");
    editBtn.disabled = true;

    initEditor();

    editBtn.style.display = "none";

    const saveBtn = document.getElementById("save-html");
    saveBtn.disabled = false;
    saveBtn.style.display = "block";

    const saveProfileBtn = document.getElementById("save-profile");
    saveProfileBtn.disabled = false;
    saveProfileBtn.style.display = "block";
}

document.getElementById('edit-html').addEventListener('click', () => {
    prepareEditor();
});

document.getElementById('save-html').addEventListener('click', () => {
    const saveBtn = document.getElementById('save-html');
    saveBtn.disabled = true;

    const pageData = {};
    const htmlContent = quills.mainQuill.root;
    const authorEL = document.getElementById("author");

    pageData.title = document.getElementById("title").textContent.slice(0, 256);
    pageData.author_name = authorEL.textContent.slice(0, 128);
    pageData.author_url = document.getElementById("link-input").innerText.slice(0, 512);
    pageData.content = JSON.stringify(domToNode(htmlContent).children);

    (async () => {
        const account = await autoCreateAccount();
        const edit = await isAllowEdit();

        if (edit) {
            const pageUri = (await getPageInfo()).path;
            r = await editPage(
                account.access_token,
                pageUri,
                new URLSearchParams(pageData).toString()
            )
            saveBtn.disabled = false;
            if (r) {
                alert("Saved Successfully!");
            } else {
                alert("Error (see logs)");
            }
        } else {
            r = await createPage(
                account.access_token,
                new URLSearchParams(pageData).toString()
            )
            saveBtn.disabled = false;
            if (r) {
                const url = `${window.location.origin}/${r.path}`;
                window.location.href = url;
            } else {
                alert("Error (see logs)");
            }
        }
        saveBtn.disabled = false;
    })();
});

document.getElementById('save-profile').addEventListener('click', () => {
    const saveBtn = document.getElementById('save-profile');
    saveBtn.disabled = true;

    const authorName = document.getElementById("author").textContent.slice(0, 128);
    const authorUrl = document.getElementById("link-input").textContent.slice(0, 512);

    (async () => {
        const account = await autoCreateAccount();

        r = await editProfileInfo(
            account.access_token,
            authorName,
            authorUrl
        )
        saveBtn.disabled = false;
        if (r) {
            alert("Updated Successfully!");
        } else {
            alert("Error (see logs)");
        }
        
        saveBtn.disabled = false;
    })();
});

document.getElementById('delete-html').addEventListener('click', () => {
    const deleteBtn = document.getElementById('delete-html');
    deleteBtn.disabled = true;

    (async () => {
        const answer = prompt(`Enter "DELETE" (without quotes)`, "");

        if (answer && ["delete", "удалить", "del", "удали"].includes(answer.toLowerCase())) {
            const account = await autoCreateAccount();
            const pageUri = (await getPageInfo()).path;

            r = await deletePage(
                account.access_token,
                pageUri
            )
            deleteBtn.disabled = false;

            if (r) {
                document.body.innerHTML = "";
                const url = `${window.location.origin}/${pageUri}`;
                window.location.href = url;
            } else {
                alert("Error (see logs)");
            }
        } else {
            alert("Canceled :>");
        }
        
        deleteBtn.disabled = false;
    })();
});

