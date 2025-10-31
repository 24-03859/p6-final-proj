// deleteNote sends a POST to /delete-note with JSON { noteID }.
// The original project either omitted this function or used the wrong
// variable name (`noteID` instead of `noteId`) which caused client-side
// JS errors and prevented deletion requests from being sent correctly.
async function deleteNote(noteId) {
    try {
        const res = await fetch('/delete-note', {
            method: 'POST',
            body: JSON.stringify({ noteID: noteId }),
            headers: { 'Content-Type': 'application/json' }
        });

        if (!res.ok) {
            console.error('Failed to delete note', res.status);
            return;
        }

        // Remove the list item from the DOM if present, otherwise reload
        const btn = document.querySelector(`#notes button[onClick*="${noteId}"]`);
        if (btn && btn.parentElement) {
            btn.parentElement.remove();
        } else {
            window.location.reload();
        }
    } catch (err) {
        console.error('Error deleting note:', err);
    }
}

window.deleteNote = deleteNote;