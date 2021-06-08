# Ergasia_2_E18086_Konstantopoulou_Elisavet
Στην 2η Υποχρεωτική Εργασία στο μάθημα Πληροφοριακά Συστήματα κληθήκαμε να υλοποιήσουμε έντεκα υποχρεωτικά endpoints (ένα από τα endpoints δημιογήθηκε χωρις να ζητείται) με τα οποία εκτελούμε ενέργειες πάνω σε μια βάση **MongoDB**. Να σημειωθεί ότι η εργασία υλοποιήθηκε σε περιβάλλον **Ubuntu 20.04** και η επεξεργασία του Python script στον **Visual Studio Code** editor. Μετά από μια σύντομη επεξήγηση του κώδικα θα ακολουθεί ένα screenshot της terminal εντολής για την υλοποίηση του εκάστοτε endpoint και τα αποτελέσματα. 

# Αρχικά Στάδια
Παρακάτω εμφανίζονται οι εντολές του terminal που εκτελέστηκαν για την **δημιουργία του 'mongodb_02' Docker container**.
```bash
sudo apt-get update 
sudo systemctl enable docker --now 
sudo usermod -aG docker $elisavetk
sudo docker pull mongo
sudo docker run -d -p 27017:27017 --name mongodb mongo
sudo docker ps -a
sudo docker start mongodb_02
python3 app_02.py
```


# Python Script 
## ENDPOINT 0 - ΔΗΜΙΟΥΡΓΙΑ ΧΡΗΣΤΗ
```python
if users.find({"email":data["email"]}).count()== 0:
        user = {"name": data['name'], "password":data['password'], "email":['email']}
        data.update({'category':'User'})
        users.insert_one(data)
        return Response(data['name']+" was added to the MongoDB", status=200, mimetype='application/json')
    else:
     return Response("A user with the given email already exists", status=401, mimetype='application/json')
```
Το endpoint αυτό δεν ζητείται στην εκφώνηση, όμως υλοποιήθηκε για να μπορεί να μπορεί να εγγραφεί κάποιος απλός χρήστης στο σύστημα. Το αξιοσημείωτο είναι το ότι αν κάποιος το κάνει αυτό, θα εισαχθεί στους 'Users', που είναι οι απλοί χρήστες. 


## ENDPOINT 1 - LOGIN
```python
if users.find_one({"$and":[{"username":data["username"]}, {"password":data["password"]}]}):
        user_uuid = create_session(data["username"])
        res = {"uuid": user_uuid, "username": data["username"]}
        return Response("Authentication successful." + json.dumps(res), mimetype='application/json', status=200)
    else:
        return Response("Wrong username or password.", status=400, mimetype='application/json')
```
Στο παραπάνω κομμάτι κώδικα ελέγχουμε εαν ο συνδυασμός του *username* και *password* που δεχτήκαμε υπάρχει στην βάση. Εάν όχι, τότε επιστρέφεται μήνυμα που ενημερώνει τον χρήστη ότι τα credentials είναι λάθος.


## ENDPOINT 2 - ΑΝΑΖΗΤΗΣΗ ΠΡΟΙΟΝΤΟΣ
```python
if "name" in data:
        search = products.find({'name':data["name"]})
        temp=[]
        for product in search:
            #allow serialization
            product['_id'] = None
            temp.append(product)
        if temp != None:    
            return Response(json.dumps(prodList, indent=4), status=200, mimetype='application/json')
```
Με την μέθοδο **find()** αναζητούμε ένα προϊόν με βάση την είσοδο του χρήστη. Εφόσον ο χρήστης μπορεί να εισάγει είτε το όνομα, είτε την κατηγορία είτε τον μοναδικό κωδικό του προϊόντος ξεκινάμε το κομμάτι αυτό με ```python if "name" in data``` που σημαίνει ότι θέτουμε σαν συνθήκη το δεδομένο που μας έδωσε ο χρήστης να είναι το όνομα ενός προϊόντος. Χρησιμοποιείτα το ```python if "category" in data``` και το ```python if "id" in data``` για να γίνει αναζήτηση με βάση την κατηγορία και τον μοναδικό κωδικό του προϊόντος, αντίστοιχα.

Ζητείται αλφανητική ταξινόμηση σε περίπτωση που ο χρήστης αναζητήσει κάποιο προϊόν με βάση την κατηγορία του................



## ENDPOINT 3 - ΠΡΟΣΘΗΚΗ ΣΤΟ ΚΑΛΑΘΙ




## ENDPOINT 4 - ΕΜΦΑΝΙΣΗ ΚΑΛΑΘΙΟΥ


## ENDPOINT 5 - ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΚΑΛΑΘΙ


## ENDPOINT 6 - ΑΓΟΡΑ ΠΡΟΙΟΝΤΩΝ


## ENDPOINT 7 - ΕΜΦΑΝΙΣΗ ΙΣΤΟΡΙΚΟΥ ΠΑΡΑΓΓΕΛΙΩΝ ΣΥΓΚΕΚΡΙΜΕΝΟΥ ΧΡΗΣΤΗ


## ENDPOINT 8 - ΔΙΑΓΡΑΦΗ ΛΟΓΑΡΙΑΣΜΟΥ
```python
student = students.update_one({"email":data["email"]}, 
{"$set":
   {
      "courses":student["courses"]
   }
})
return Response("Courses added.", status=200, mimetype='application/json')
```
Με την χρήση της μεθόδου **_update_one()_** προσθέτουμε, κατά μια έννοια, courses σύμφωνα με τον τρόπο που αναγράφεται στην εκφώνηση.



## ENDPOINT 9 - ADMIN: ΕΙΣΑΓΩΓΗ ΝΕΟΥ ΠΡΟΙΟΝΤΟΣ
```python
for course in courses.values():
   for item in course:
      for grade in item:
         if item.get(grade)>=5:      
            student[grade]=item.get(grade)
            return Response("The student has passed the following courses: " + json.dumps(student), status=200, mimetype='application/json')
```
Το αξιοσημείωτο στο ENDPOINT 9  είναι τα *nested for loops*, καθώς η συνθήκη για να εκτελεστεί ο παραπάνω κώδικας είναι αρχικά η αυθεντικοποίηση του χρήστη και μετά η αντίστοιχη εντολή **_find_one()_** του ENDPOINT 6, απλά με τα ορίσματα *{"email":data["email"]}* και *{"courses":{"$ne":None}}*. 

Ο στόχος ήταν να **απομονώσουμε** το κάθε μάθημα με τις προσπελάσεις αυτές και να πάρουμε μόνο τον βαθμό για να τον συγκρίνουμε με το 5. Εάν ο βαθμός είναι μεγαλύτερος ή ίσος του 5, τότε το μάθημα είναι περασμένο και όλο το αντίστοιχο course (όνομα μαθήματος & βαθμός) περνάει στον πίινακα student. 
Τέλος εμφανίζουμε τον πίνακα student.



## ENDPOINT 10 - ADMIN: ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΣΥΣΤΗΜΑ
```python
for course in courses.values():
   for item in course:
      for grade in item:
         if item.get(grade)>=5:      
            student[grade]=item.get(grade)
            return Response("The student has passed the following courses: " + json.dumps(student), status=200, mimetype='application/json')
```
Το αξιοσημείωτο στο ENDPOINT 9  είναι τα *nested for loops*, καθώς η συνθήκη για να εκτελεστεί ο παραπάνω κώδικας είναι αρχικά η αυθεντικοποίηση του χρήστη και μετά η αντίστοιχη εντολή **_find_one()_** του ENDPOINT 6, απλά με τα ορίσματα *{"email":data["email"]}* και *{"courses":{"$ne":None}}*. 

Ο στόχος ήταν να **απομονώσουμε** το κάθε μάθημα με τις προσπελάσεις αυτές και να πάρουμε μόνο τον βαθμό για να τον συγκρίνουμε με το 5. Εάν ο βαθμός είναι μεγαλύτερος ή ίσος του 5, τότε το μάθημα είναι περασμένο και όλο το αντίστοιχο course (όνομα μαθήματος & βαθμός) περνάει στον πίινακα student. 
Τέλος εμφανίζουμε τον πίνακα student.



## ENDPOINT 11 - ADMIN: ΕΝΗΕΡΩΣΗ ΠΡΟΙΟΝΤΟΣ
```python
for course in courses.values():
   for item in course:
      for grade in item:
         if item.get(grade)>=5:      
            student[grade]=item.get(grade)
            return Response("The student has passed the following courses: " + json.dumps(student), status=200, mimetype='application/json')
```
Το αξιοσημείωτο στο ENDPOINT 9  είναι τα *nested for loops*, καθώς η συνθήκη για να εκτελεστεί ο παραπάνω κώδικας είναι αρχικά η αυθεντικοποίηση του χρήστη και μετά η αντίστοιχη εντολή **_find_one()_** του ENDPOINT 6, απλά με τα ορίσματα *{"email":data["email"]}* και *{"courses":{"$ne":None}}*. 

Ο στόχος ήταν να **απομονώσουμε** το κάθε μάθημα με τις προσπελάσεις αυτές και να πάρουμε μόνο τον βαθμό για να τον συγκρίνουμε με το 5. Εάν ο βαθμός είναι μεγαλύτερος ή ίσος του 5, τότε το μάθημα είναι περασμένο και όλο το αντίστοιχο course (όνομα μαθήματος & βαθμός) περνάει στον πίινακα student. 
Τέλος εμφανίζουμε τον πίνακα student.

