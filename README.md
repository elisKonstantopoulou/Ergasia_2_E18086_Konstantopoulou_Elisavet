# Ergasia_2_E18086_Konstantopoulou_Elisavet
Στην 2η Υποχρεωτική Εργασία στο μάθημα Πληροφοριακά Συστήματα κληθήκαμε να υλοποιήσουμε έντεκα υποχρεωτικά endpoints (ένα από τα endpoints δημιογήθηκε χωρις να ζητείται) με τα οποία εκτελούμε ενέργειες πάνω σε μια βάση **MongoDB**. Να σημειωθεί ότι η εργασία υλοποιήθηκε σε περιβάλλον **Ubuntu 20.04** και η επεξεργασία του Python script στον **Visual Studio Code** editor. Μετά από μια σύντομη επεξήγηση του κώδικα θα ακολουθεί ένα screenshot της terminal εντολής για την υλοποίηση του εκάστοτε endpoint και τα αποτελέσματα. 

# Αρχικά Στάδια
Παρακάτω εμφανίζονται οι εντολές του terminal που εκτελέστηκαν για την **δημιουργία του 'mongodb_02' Docker container**.
```bash
sudo apt-get update 
sudo systemctl enable docker --now 
sudo usermod -aG docker $elisavetk
sudo docker pull mongo
sudo docker run -d -p 27017:27017 --name mongodb_02 mongo
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
Με την μέθοδο **_find()_** αναζητούμε ένα προϊόν με βάση την είσοδο του χρήστη. Εφόσον ο χρήστης μπορεί να εισάγει είτε το όνομα, είτε την κατηγορία είτε τον μοναδικό κωδικό του προϊόντος ξεκινάμε το κομμάτι αυτό με ```python if "name" in data``` που σημαίνει ότι θέτουμε σαν συνθήκη το δεδομένο που μας έδωσε ο χρήστης να είναι το όνομα ενός προϊόντος. Χρησιμοποιείτα το ```python if "category" in data``` και το ```python if "id" in data``` για να γίνει αναζήτηση με βάση την κατηγορία και τον μοναδικό κωδικό του προϊόντος, αντίστοιχα.

Ζητείται αλφανητική ταξινόμηση σε περίπτωση που ο χρήστης αναζητήσει κάποιο προϊόν με βάση την κατηγορία του................



## ENDPOINT 3 - ΠΡΟΣΘΗΚΗ ΣΤΟ ΚΑΛΑΘΙ




## ENDPOINT 4 - ΕΜΦΑΝΙΣΗ ΚΑΛΑΘΙΟΥ


## ENDPOINT 5 - ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΚΑΛΑΘΙ


## ENDPOINT 6 - ΑΓΟΡΑ ΠΡΟΙΟΝΤΩΝ


## ENDPOINT 7 - ΕΜΦΑΝΙΣΗ ΙΣΤΟΡΙΚΟΥ ΠΑΡΑΓΓΕΛΙΩΝ ΣΥΓΚΕΚΡΙΜΕΝΟΥ ΧΡΗΣΤΗ


## ENDPOINT 8 - ΔΙΑΓΡΑΦΗ ΛΟΓΑΡΙΑΣΜΟΥ
```python
user = users.find_one({'email':data["email"]})
    #does user with the given id exist?
    if user != None:
        #Deleting the user from the collection 'users'
        users.delete_one(user)
        username = user["name"]
        #Passing the user's name and the string " was deleted" to variable msg
        msg = username['name'] + " was deleted successfully"
        return Response(msg, status=200, mimetype='application/json')
    else:
        return Response("No product with that id was found", status=500, mimetype='application/json')
```
Με την χρήση της μεθόδου **_delete_one()_** διαγράφουμε τον χρήστη που έχει το email που δόθηκε ως είσοδος και επιστρέφεται μήνυμα ότι ο συγκεκριμένος χρήατης (εμφανίζει το όνομα του χρήστη) έχει διαγραφεί με επιτυχία.



## ENDPOINT 9 - ADMIN: ΕΙΣΑΓΩΓΗ ΝΕΟΥ ΠΡΟΙΟΝΤΟΣ
```python
    #store the product in the product dictionary
    product = {"name": data['name'], "category": data['category'], "quantity":['quantity'], "description":['description'], "price":['price']}
    #inserting them in Products collection
    products.insert_one(product)
    #response
    return Response(data['name'] + " was added to the MongoDB", status=200, mimetype='application/json')
```
Για να εισαχθεί νέο προϊόν από τον admin πρέπει να εισαχθούν το όνομά, ηκατηγορία, η ποσότητα, η περιγραφή και η τιμή του. Όλα αυτά τα δεδομένα που εισάγει ο χρήστης ,μπαίνουν στην μεταβλητή product και μετά το προϊόν αυτό εισάγεται στο 'products' με την χρήση της μεθόδου **_insert_one()_**.



## ENDPOINT 10 - ADMIN: ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΣΥΣΤΗΜΑ
```python
 # find product through id and put the result to dictionary product 
    product = products.find_one({"product_id":data['product_id']})
    # does the product with the given id exist?
    if product != None:
        products.delete_one(product)
        #Passing the product's name and the string " was deleted" to variable msg
        msg = product['name'] + " was deleted successfully"
        return Response(msg, status=200, mimetype='application/json')
    else:
        return Response("No product with that id was found", status=500, mimetype='application/json')
```
Με την μέθοδο **_find_one()_** αναζητούμε ένα προϊόν με βάση το id του και με την χρήση της μεθόδου **_delete_one()_** διαγράφουμε το προϊόν αυτό και επιστρέφεται μήνυμα ότι το συγκεκριμένο προϊόν (εμφανίζει το όνομα του προϊόντος) έχει διαγραφεί με επιτυχία.




## ENDPOINT 11 - ADMIN: ΕΝΗΜΕΡΩΣΗ ΠΡΟΙΟΝΤΟΣ
```python
if product != None:
        if "name" in data:
            product.update_one({'id':data["data"]}, {'$set':{'name':data["name"]}})
        if "price" in data:
            product.update_one({'id':data["data"]}, {'$set':{'price':data["price"]}})
        if "description" in data:
            product.update_one({'id':data["data"]}, {'$set':{'description':data["description"]}})
        if "stock" in data:
            product.update_one({'id':data["data"]}, {'$set':{'stock':data["stock"]}})
        #Passing the product's name and the string " was edited successfully" to variable msg
        msg = product['name'] + " was edited successfully"
        return Response(msg, status=200, mimetype='application/json')
    else:
        return Response("No product with that id was found", status=500, mimetype='application/json')
```
Δίνεται ως είσοδος ο μοναδικός κωδικός του πρϊόντος και αν βρεθεί προϊόν με τέτοιον κωδικό τότε ένα από τα πεδία που εισάγει ο admin (όνομα, τιμή, περιγραφή, απόθεμα) θα ενημερωθούν. Μόλις γίνει αυτό, επιστρέφεται μήνυμα επιτυχούς αλλαγής του προϊόντος μαζί με το όνομά του. Σε διαφορετική περίπτωση, δηλαδή σε περίπτωση που δεν υπήρχε προϊόν με τέτοιον μοναδικό κωδικό, επιστρέφεται το αντίστοιχο μήνυμα λάθους.

