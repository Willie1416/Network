document.addEventListener('DOMContentLoaded', function() {

    // Event listener for eahc edit button
    document.querySelectorAll('.edit').forEach(button => {
        button.addEventListener('click', function(){
            const post_id = this.getAttribute('data-post-id');
            load_edit(post_id);
        });
    });

    // Event listener for each like button
    document.querySelectorAll('.like').forEach(button => {
        button.addEventListener('click', function(){
            const post_id = this.getAttribute('data-post-id');
            like(post_id);
        });
    });
});


function load_edit(post_id){
    // Get the content from post
    const content = document.querySelector(`#content-${post_id}`);
    const editButton = document.querySelector(`#edit-${post_id}`);
    const timestamp = document.querySelector(`#timestamp-${post_id}`);

    // Hide the content and edit button
    content.style.display = 'none';
    editButton.style.display = 'none'

    // Create a textarea and prepopulate with content
    const new_content = document.createElement("textarea");
    new_content.id = `textarea-${post_id}`;  // Unique ID for the textarea
    new_content.value = content.textContent;

    // Create a save button to save the new content
    const save = document.createElement("button");
    save.id = `save-${post_id}`;  // Unique ID for the save button
    save.textContent = "Save";
    save.className = "btn btn-primary mt-2 p-1";

    // Put the new elements into the DOM
    content.parentNode.replaceChild(new_content, content);
    new_content.parentNode.insertBefore(save, new_content.nextSibling);

    new_content.focus();

    // Add an event listnere to the save button
    save.addEventListener('click', function(){

        // Get the updated content
        const updatedContent = new_content.value

        fetch(`/update/${post_id}`,{
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: updatedContent,
            })
        })
        .then(response => response.json())
        .then(data => {
            
            // Update the content div with the new content
            content.textContent = updatedContent;
            timestamp.textContent = data.timestamp;

            // Restore the original view
            new_content.parentNode.replaceChild(content, new_content)
            content.style.display = 'block';
            editButton.style.display = 'block'
            save.remove()
        
        })
        .catch(error => {
            console.log(error)
        });
    });
}

function like(post_id){
    
    // Get the post the liked button was clicked on
    const like_count = document.querySelector(`#like-${post_id}`)

    // Make a fetch call that check if the post is to be liked or unliked depending on status
    fetch(`/like/${post_id}`,{
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        
        // Update the like count
        like_count.innerHTML = `&hearts; ${data.like_count}`
    
    })
    .catch(error => {
        console.log(error)
    });

}