from flask import Flask, render_template, request,session

app = Flask(__name__)
app.secret_key = 'debug_notetaking__app'


@app.route('/', methods=["GET","POST"])
def index():
    if 'notes' not in session:
       
        session['notes'] = []
    notes = session['notes']
    if request.method=='POST':
        
        if 'Clear' in request.form:
            session['notes'] = []
            notes = []
        
        elif 'note_to_remove' in request.form:
            note_to_remove = request.form['note_to_remove']
            notes.remove(note_to_remove)
            session['notes'] = notes
            
        else:
            note = request.form.get('note')
        
            if note and note.strip():

                notes.append(note.strip())
                session['notes']=notes
                
    return render_template("home.html", notes=notes)


if __name__ == '__main__':
    app.run(debug=True)