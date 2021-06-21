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
## ΠΡΩΤΟΒΟΥΛΙΕΣ
Ελήφθησαν οι παρακάτω πρωτοβουλίες στην εκπόνιση της εργασίας:
* Το όνομα του χρήστη στο σύστημα/πρόγραμμα είναι το *username*
* Η αυθεντικοποίηση των χρηστών (simple users, admin) να γίνεται με username και password
* Η αυθεντικοποίηση των χρηστών (είτε simple users ή admin) πραγματοποιείται πριν από κ=την εκτέλεση των εντολών των endpoints
* Οι admin πρέπει να κάνουν login στο σύστημα
* Γίνεται έλεγχος σε κάθε endpoint, εάν ο χρήστης που χησιμοποιεί την εκάστοτε στιγμή το πρόγραμα είναι simple user ή admin, έτσι ώστε να μην μπορεί ένα απλός χρήστης να εκτελέσει τα endpoints ενός διαχειριστή, και το ανάποδο

## ENDPOINT 0 - ΔΗΜΙΟΥΡΓΙΑ ΧΡΗΣΤΗ
```python
if users.find({"email":data["email"]}).count()== 0:
        user = {"username": data['username'], "password":data['password'], "email":data['email']}
        if data['username']=="admin":
            data.update({'category':'Admin'})
            users.insert_one(data)
            return Response("Admin was added to the MongoDB", status=200, mimetype='application/json')
        else:
            data.update({'category':'User'})
            total=0
            data.update({'cart':[{'total':total}]})
            data.update({'orderHistory':[]})
            users.insert_one(data)
            return Response("Simple user " + data['username']+" was added to the MongoDB", status=200, mimetype='application/json')            
    else:
     return Response("A user with the given email already exists", status=401, mimetype='application/json')
```
Το endpoint αυτό δεν ζητείται στην εκφώνηση, όμως υλοποιήθηκε για την εισαγωγή χρηστών στην βάση του συστήματος. Το αξιοσημείωτο είναι το ότι αν κάποιος βάλει σαν username το **_'admin'_** θα εγγραφεί ως Admin στο σύστημα (επομένως το πεδίο category θα έχει την τιμή Admin), αλλιώς θα εισαχθεί στους 'Users' ως απλός χρήστης. Στα παρακάτω screenshots βλέπουμε πρώτα την δημιουργία δύο απλών χρηστών και μετά την δημιουργία ενός διαχειριστή.

<img src="/ergasia_2_screenshots/00_createUser/creatingUsers.png" width=100%>
<img src="/ergasia_2_screenshots/00_createUser/users_when_created.png" width=30%>
<img src="/ergasia_2_screenshots/00_createUser/admin_created.png" width=100%>

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
Στα παρακάτω csreenshots βλέπουμε πρώτα το login ενός απλού χρήστη και μετά το login ενός διαχειριστή.
<img src="/ergasia_2_screenshots/01_login/user_1_logged_in.png" width=100%>
<img src="/ergasia_2_screenshots/01_login/endpoint_admin_00_login.png" width=100%>

## ENDPOINT 2 - ΑΝΑΖΗΤΗΣΗ ΠΡΟΙΟΝΤΟΣ
```python
elif "category" in data:
                search = products.find({'category':data["category"]})
                temp=[]
                for product in search:
                    #allow serialization
                    product['_id'] = None
                    temp.append(product)
                if temp != None:     
                    sort = sorted(temp, key = lambda i: i['price'])
                    return Response(json.dumps(sort, indent=4), status=200, mimetype='application/json')   
```
Με την μέθοδο **_find()_** αναζητούμε ένα προϊόν με βάση την είσοδο του χρήστη. Εφόσον ο χρήστης μπορεί να εισάγει είτε το όνομα, είτε την κατηγορία είτε τον μοναδικό κωδικό του προϊόντος ξεκινάμε το κομμάτι αυτό με ```python if "name" in data``` που σημαίνει ότι θέτουμε σαν συνθήκη το δεδομένο που μας έδωσε ο χρήστης να είναι το όνομα ενός προϊόντος. Χρησιμοποιείτα το ```python if "category" in data``` και το ```python if "id" in data``` για να γίνει αναζήτηση με βάση την κατηγορία και τον μοναδικό κωδικό του προϊόντος, αντίστοιχα.

<img src="/ergasia_2_screenshots/02_user_searchProduct/endpoint_03_searchProduct.png" width=100%>

## ENDPOINT 3 - ΠΡΟΣΘΗΚΗ ΣΤΟ ΚΑΛΑΘΙ
```python 
new_quantity = int(data['quantity'])
if new_quantity<=int(product['quantity']):
        if not 'cart' in currUser:
                temporary_cart = [0] 
                temporary_cart.append({data["productID"]: data["quantity"]})
                temporary_cart[0] = temporary_cart[0]+float(product['price'])*float(data['quantity'])
                users.update_one({"email":data['email']},{"$set": {"cart":temporary_cart}})
                total = temporary_cart[0]
                return Response(json.dumps(temporary_cart, indent=3), status=200, mimetype='application/json')
        else: 
                temporary_cart = currUser['cart']
                for i in range(1, len(temporary_cart)): # search if same product already in cart
                        if list(temporary_cart[i].keys())[0] == data['productID']:
                                return Response("You already have that product!", status=400, mimetype='application/json')
                        temporary_cart.append({product["productID"]:data["quantity"]})
                        temporary_cart[0] = temporary_cart[0]+float(product['price'])*float(data['quantity']) 
                        users.update_one({"email":data['email']},{"$set": {"cart":temporary_cart}})
                        total = currUser['cart'][0]
                        return Response(json.dumps(temporary_cart, indent=3), status=200, mimetype='application/json')                        
else:
        return Response("Insufficient stock!",status=500,mimetype="application/json")
```
Μετά την αυθεντικοποίηση του χρήστη, τον έλεγχο για το εάν είναι απλός χρήστης και τον έλεγχο ύπαρξης του προϊόντος, εκτελούνται οι εντολές για την εισαγωγή δοθέντος ποροϊόντος στο καλάθι του χρήστη. Πρώτα γίνεται έλεγχος αν το stock του συγκεκριμένου προϊόντος επαρκεί για την αγορά και ύστερα, έχουμε δύο περιπτώσεις:
1. Αυτή να είναι η πρώτη αγορά του χρήστη, επομένως δεν υπάρχει καλάθι
        * Στην περίπτωση αυτή, δημιουργούμε πρώτα ένα προσωρινό καλάθι, με το πρώτο στοιχείο του να είναι ίσο με μηδέν (αντιπροσωπεύει το συνολικό κόστος του καλαθιού).
        * Με την χρήση του **_append()_**, προσθέτουμε στην αμέσως επόμενη θέση του προσωρινού καλαθιού το **poductID** και την **τιμή** του προϊόντος.
        * Αλλάζουμε την τιμή του συνόλου του καλαθιού με το να πολλαπλασιάσουμε την ποσότητα που εισήγαγε ο χρήστης με την τιμή του προΙόντος
        * Περνάμε στο προσωρινό καλάθι στο dictionary *cart* που δημιουργήθηκε στον χρήστη
        * Τέλος, επιστρέφουμε το καλάθι
2. Αυτή να μην είναι η πρώτη αγορά του χήστη, επομένως υπάρχει ήδη καλάθι 
        * Στην περίπτωση αυτή, ψάχνουμε το καλάθι, μήπως έχει ήδη μέσα το προϊόν που εισήγαγε ο χρήστης.
        * Εάν το έχει, επιστρέφεται μήνυμα ότι το προϊόν υπάρχει ήη στο καλάθι.
        * Εάν δεν το έχει, ακολουθούνται τα ίδια βήματα με την παραπάνωπερίπτωση.
 
<img src="/ergasia_2_screenshots/03_user_addToCart/adding_two_products_in_cart.png" width=100%>

## ENDPOINT 4 - ΕΜΦΑΝΙΣΗ ΚΑΛΑΘΙΟΥ
```python 
currUser = users.find_one({'email':data["email"]})
        if currUser != None:
            flag2 = currUser.get('category')
            if flag2=="User":            
                return Response("User's Cart: " + json.dumps(currUser['cart'], indent=4))
            else:
                return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
        else:
            return Response("No user found!")
```
Εφόσον το email που δίνεται από τον χρήστη αντιστοιχεί σε κάποιον χρήστη, ο οποίος είναι και απλός χρήστης, τότε επιστρέφεται το καλάθι.

<img src="/ergasia_2_screenshots/04_user_viewCart/viewCart.png" width=100%>

## ENDPOINT 5 - ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΚΑΛΑΘΙ
```python 
currUser = users.find_one({'email':data["email"]})
        if currUser != None:
            flag2 = currUser.get('category')
            if flag2=="User":            
                return Response("User's Cart: " + json.dumps(currUser['cart'], indent=4))
            else:
                return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
        else:
            return Response("No user found!")
```

## ENDPOINT 8 - ΔΙΑΓΡΑΦΗ ΧΡΗΣΤΗ
```python
user = users.find_one({'email':data["email"]})
    if user != None:
        users.delete_one(user)
        username = user["name"]
        msg = username['name'] + " was deleted successfully"
        return Response(msg, status=200, mimetype='application/json')
    else:
        return Response("No product with that id was found", status=500, mimetype='application/json')
```
Με την χρήση της μεθόδου **_delete_one()_** διαγράφουμε τον χρήστη που έχει το email που δόθηκε ως είσοδος και επιστρέφεται μήνυμα ότι ο συγκεκριμένος χρήατης (εμφανίζει το όνομα του χρήστη) έχει διαγραφεί με επιτυχία.

<img src="/ergasia_2_screenshots/08_user_deleteUser/endpoint_deleteUser.png" width=100%>
<img src="/ergasia_2_screenshots/08_user_deleteUser/endpoint_deleteUserr.png" width=30%>
<img src="/ergasia_2_screenshots/08_user_deleteUser/endpoint_deleteUserrr.png" width=30%>

## ENDPOINT 9 - ADMIN: ΕΙΣΑΓΩΓΗ ΝΕΟΥ ΠΡΟΙΟΝΤΟΣ
```python
    product = {"name": data['name'], "category": data['category'], "quantity":['quantity'], "description":['description'], "price":['price']}
    products.insert_one(product)
    return Response(data['name'] + " was added to the MongoDB", status=200, mimetype='application/json')
```
Για να εισαχθεί νέο προϊόν από τον admin πρέπει να εισαχθούν το όνομά, ηκατηγορία, η ποσότητα, η περιγραφή και η τιμή του. Όλα αυτά τα δεδομένα που εισάγει ο χρήστης ,μπαίνουν στην μεταβλητή product και μετά το προϊόν αυτό εισάγεται στο 'products' με την χρήση της μεθόδου **_insert_one()_**.

<img src="/ergasia_2_screenshots/09_admin_insertProduct/endpoint_admin_01_insertProduct(1).png" width=100%>
<img src="/ergasia_2_screenshots/09_admin_insertProduct/endpoint_admin_01_insertProduct(2).png" width=100%>

## ENDPOINT 10 - ADMIN: ΔΙΑΓΡΑΦΗ ΠΡΟΙΟΝΤΟΣ ΑΠΟ ΤΟ ΣΥΣΤΗΜΑ
```python
    product = products.find_one({"product_id":data['product_id']})
    if product != None:
        products.delete_one(product)
        msg = product['name'] + " was deleted successfully"
        return Response(msg, status=200, mimetype='application/json')
    else:
        return Response("No product with that id was found", status=500, mimetype='application/json')
```
Με την μέθοδο **_find_one()_** αναζητούμε ένα προϊόν με βάση το id του και με την χρήση της μεθόδου **_delete_one()_** διαγράφουμε το προϊόν αυτό και επιστρέφεται μήνυμα ότι το συγκεκριμένο προϊόν (εμφανίζει το όνομα του προϊόντος) έχει διαγραφεί με επιτυχία.

<img src="/ergasia_2_screenshots/10_admin_deleteProduct/endpoint_admin_02_deleteProduct(1).png" width=100%>
<img src="/ergasia_2_screenshots/10_admin_deleteProduct/endpoint_admin_02_deleteProduct(2).png" width=50%>

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
        msg = product['name'] + " was edited successfully"
        return Response(msg, status=200, mimetype='application/json')
    else:
        return Response("No product with that id was found", status=500, mimetype='application/json')
```
Δίνεται ως είσοδος ο μοναδικός κωδικός του πρϊόντος και αν βρεθεί προϊόν με τέτοιον κωδικό τότε ένα από τα πεδία που εισάγει ο admin (όνομα, τιμή, περιγραφή, απόθεμα) θα ενημερωθούν. Μόλις γίνει αυτό, επιστρέφεται μήνυμα επιτυχούς αλλαγής του προϊόντος μαζί με το όνομά του. Σε διαφορετική περίπτωση, δηλαδή σε περίπτωση που δεν υπήρχε προϊόν με τέτοιον μοναδικό κωδικό, επιστρέφεται το αντίστοιχο μήνυμα λάθους.

<img src="/ergasia_2_screenshots/11_admin_editProduct/endpoint_admin_03_editProduct(1).png" width=100%>
<img src="/ergasia_2_screenshots/11_admin_editProduct/endpoint_admin_03_editProduct(2).png" width=80%>
