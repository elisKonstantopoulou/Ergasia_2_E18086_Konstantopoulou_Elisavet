from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')
# Choose database
db = client['DSMarkets']
# Choose collections
users = db['Users']
products = db['Products']
# Initiate Flask App
app = Flask(__name__)
users_sessions = {}
def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  
def is_session_valid(user_uuid):
    return user_uuid in users_sessions

# ΔΗΜΙΟΥΡΓΙΑ ΧΡΗΣΤΗ ===============================================================================================================
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    # check if user with same email exists in database
    if users.find({"email":data["email"]}).count()== 0: # if there is none, create one with the username and password we got from terminal
        user = {"username": data['username'], "password":data['password'], "email":data['email']}
        # if someone wants to be an admin in this system, then their username has to be 'admin'
        # assign categories to users according to their usernames
        if data['username']=="admin":
            data.update({'category':'Admin'})
            users.insert_one(data)
            return Response("Admin was added to the MongoDB", status=200, mimetype='application/json')
        else:
            data.update({'category':'User'})
            users.insert_one(data)
            return Response("Simple user " + data['username']+" was added to the MongoDB", status=200, mimetype='application/json')            
    else:
     return Response("A user with the given email already exists", status=401, mimetype='application/json')

# LOGIN ===========================================================================================================================
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    # if the pair of username and password the user gives matches one that exists in the database, the user is authenticated
    if users.find_one({"$and":[{"username":data["username"]}, {"password":data["password"]}]}):
        user_uuid = create_session(data["username"])
        res = {"uuid": user_uuid, "username": data["username"]}
        return Response("Authentication successful." + json.dumps(res), mimetype='application/json', status=200)
    else:
        return Response("Wrong username or password.", status=400, mimetype='application/json')

# ΑΝΑΖΗΤΗΣΗ ΠΡΟΪΟΝΤΟΣ =============================================================================================================
@app.route('/searchProduct', methods=['GET'])
def search_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data: #look again to add name,category and productID
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    # user authentication - sae thing happens to the rest of the endpoints
    if flag:
        currUser = users.find_one({'email':data["email"]})
        flag2 = currUser.get('category')
        # user category authentication --> must be 'User' - same thing happens to all user endpoints
        if flag2=="User":
            if "name" in data: # if user gives name of a product 
                search = products.find({'name':data["name"]})
                temp=[]
                for product in search:
                    #allow serialization
                    product['_id'] = None
                    temp.append(product)
                if temp != None:    
                    return Response(json.dumps(prodList, indent=4), status=200, mimetype='application/json')  
            elif "category" in data: # if user gives category of a product 
                search = products.find({'category':data["category"]})
                temp=[] # array to help us sort products
                for product in search:
                    #allow serialization
                    product['_id'] = None
                    temp.append(product)
                if temp != None:     
                    sort = sorted(temp, key = lambda i: i['price'])
                    return Response(json.dumps(sort, indent=4), status=200, mimetype='application/json')      
            elif "productID" in data: # if user gives id of a product 
                search = products.find({'productID':data["productID"]})
                temp=[]
                for product in search:
                    #allow serialization
                    product['_id'] = None
                    temp.append(product)
                if temp != None: 
                    return Response(json.dumps(temp, indent=4), status=200, mimetype='application/json')
        else:
            return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
    else:
        return Response("User not authenticated.", status=401, mimetype='application/json')

# ΠΡΟΣΘΗΚΗ ΠΡΟΪΟΝΤΩΝ ΣΤΟ ΚΑΛΑΘΙ ===================================================================================================
@app.route('/addToCart', methods=['PATCH'])
def add_to_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "productID" in data or not "quantity" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)
    if flag:
        currUser = users.find_one({'email':data["email"]}) # find user with given email
        if currUser != None:
            flag2 = currUser.get('category') # put category in this variable
            if flag2=="User": # if the user is a simple user
                product = products.find_one({"productID":data["productID"]}) # find the product the user added
                if product != None: # if given product exists
                    new_quantity = int(data['quantity']) # quantity the user gives
                    if new_quantity<=int(product['quantity']): # if stock suffices
                        if not 'cart' in currUser: # if user doesn't have a cart (first product)
                            temporary_cart = [0] # store the cart here temporarily, with first element = 0
                            temporary_cart.append({data["productID"]: data["quantity"]})
                            temporary_cart[0] = temporary_cart[0]+float(product['price'])*float(data['quantity'])
                            users.update_one({"email":data['email']},{"$set": {"cart":temporary_cart}})
                            #Assigning to total var the price
                            total = temporary_cart[0]
                            return Response(json.dumps(temporary_cart, indent=3), status=200, mimetype='application/json')
                        else: # user already has a cart
                            temporary_cart = currUser['cart']
                            for i in range(1, len(temporary_cart)): # search if same product already in cart
                                if list(temporary_cart[i].keys())[0] == data['productID']:
                                    return Response("You already have that product!", status=400, mimetype='application/json')
                            # add to temporary cart a dictionary with a productID and quantity key-value pair
                            temporary_cart.append({product["productID"]:data["quantity"]})
                            temporary_cart[0] = temporary_cart[0]+float(product['price'])*float(data['quantity'])
                            # update in dictionary 
                            users.update_one({"email":data['email']},{"$set": {"cart":temporary_cart}})
                            total = currUser['cart'][0]
                            return Response(json.dumps(temporary_cart, indent=3), status=200, mimetype='application/json')                        
                    else:
                        return Response("Insufficient stock!",status=500,mimetype="application/json")
                else:
                    return Response("Incorrect product ID!",status=500,mimetype="application/json")
            else:
                return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
        else:
            return Response("No user with given email.", status=401, mimetype='application/json') 
    else:
        return Response("User not authenticated.", status=401, mimetype='application/json')

# ΕΜΦΑΝΣΗ ΚΑΛΑΘΙΟΥ ================================================================================================================
@app.route('/viewCart', methods=['GET'])
def view_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')

    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    if flag:
        currUser = users.find_one({'email':data["email"]}) # find user by email
        if currUser != None:
            flag2 = currUser.get('category')
            if flag2=="User":            
                return Response("User's Cart: " + json.dumps(currUser['cart'], indent=4))
            else:
                return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
        else:
            return Response("No user found!")    
    else:
        return Response("User not authenticated.", status=401, mimetype='application/json')

# ΔΙΑΓΡΑΦΗ ΠΡΟΪΟΝΤΩΝ ΑΠΟ ΤΟ ΚΑΛΑΘΙ ================================================================================================
@app.route('/deleteFromCart', methods=['DELETE'])
def delete_from_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "productID" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    if flag:
        currUser = users.find_one({'email':data["email"]}) # find user by email
        flag2 = currUser.get('category')
        if flag2=="User":
            product = products.find_one({"productID":data["productID"]}) # find the product the user added
            if product != None: # if product with given id exists
                if not 'cart' in currUser: # if user has no cart
                    return Response("No cart found!", status=500, mimetype='application/json')
                else:
                    temporary_cart=currUser["cart"] # store cart in temporary table
                    flag3 = False
                    pointer = 0
                    for i in range(1, len(temporary_cart)): 
                        if list(temporary_cart[i].keys())[0] == data['productID']: # search if same product already in cart
                            flag3=True
                            pointer = i
                            break
                    if flag3==True: # the product was found in the cart
                        # update cart total --> total = total - (quantity user gave * product price)
                        temporary_cart[0] = temporary_cart[0] - float(product['price']) * float(temporary_cart[pointer].get(data['productID']))
                        # remove product
                        temporary_cart.pop(pointer)                          
                        # update dictionary 
                        currUser = users.update_one({'email':data['email']}, {"$set":{"cart":temporary_cart}})
                        return Response(json.dumps(temporary_cart, indent=3), status=200, mimetype='application/json')                            
                    else: # the product wasn't found in the cart
                        return Response("No such product in cart!",status=500,mimetype="application/json")      
            else:
                return Response("Incorrect product ID!",status=500,mimetype="application/json")
        else:
            return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
    else:
        return Response("User not authenticated.", status=401, mimetype='application/json')

# ΑΓΟΡΑ ================================================================================================================
@app.route('/buy', methods=['PATCH'])
def buy():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "card" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')

    # To - Do:
    # get user and card
    # store user's cart in temporary array (if cart exists)
    # get the total and display it along with the contents of the cart

    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    if flag:
        currUser = users.find_one({'email':data["email"]})
        if currUser != None:
            flag2 = currUser.get('category')
            if flag2=="User":
                if len(data["card"])==16:
                    if not 'cart' in currUser: # if user has no cart
                        return Response("Can't check out, no cart found!", status=500, mimetype='application/json')
                    else:
                        temporary_cart=currUser["cart"] # store cart in temporary table
                        total = currUser['cart'][0]
                        orders = [] # temporary array with smilar use to temporary_cart
                        if 'order_history' in currUser:
                            orders = currUser['order_history']
                        orders.append(temporary_cart)
                        # adding an order_history to the user
                        users.update_one({"email":data['email']},{"$set":{"order_history":orders}})
                        # removing the cart from the user since after chekout the cart disappears
                        users.update_one({"email":data['email']}, {"$unset":{"cart":""}})
                        return Response("Checkout Successful.\nThank you for your purchase!\nRECEIPT:\nPRODUCT ID : QUANTITY\n"+json.dumps(temporary_cart, indent=4) + "\nTOTAL: " + json.dumps(total), status=200, mimetype='application/json')
                else:
                    return Response("Invalid card number!", status=401, mimetype='application/json')
            else:
                return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
        else:
            return Response("No user found!")    
    else:
        return Response("User not authenticated.", status=401, mimetype='application/json')

# ΕΜΦΑΝΣΗ ΙΣΤΟΡΙΚΟΥ ΠΑΑΓΓΕΛΙΩΝ ====================================================================================================
@app.route('/viewOrderHistory', methods=['GET'])
def view_order_history():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')

    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)
    # similar logic to the viewCart endpoint
    if flag:
        currUser = users.find_one({'email':data["email"]})
        if currUser != None:
            flag2 = currUser.get('category')
            if flag2=="User":
                if not 'order_history' in currUser: # user hasn't made any purchases
                    return Response("There are no previous orders!", status=401, mimetype='application/json')
                else:
                    temporary_history = currUser['order_history'] # storing it temporarily (same logic as temporary_cart)
                    return Response("ORDER HISTORY:\n " + json.dumps(currUser['order_history'], indent=4))
            else:
                return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
        else:
            return Response("No user found!")    
    else:
        return Response("User not authenticated.", status=401, mimetype='application/json')

# ΔΙΑΓΡΑΦΗ ΧΡΗΣΤΗ =================================================================================================================
@app.route('/deleteUser', methods=['DELETE'])
def delete_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    if flag:
        currUser = users.find_one({'email':data["email"]})
        flag2 = currUser.get('category')
        if flag2=="User":
            # finding the user through email 
            user = users.find_one({'email':data["email"]})
            # checking if a user with the given email exists
            if user != None:
                # deleting the user from the collection
                users.delete_one(user)
                # passing the user's name and the string " was deleted" to variable msg
                msg = user['username'] + " was deleted successfully"
                return Response(msg, status=200, mimetype='application/json')
            # no user with the given email
            else:
                return Response("No user with that email was found", status=500, mimetype='application/json')
        else:
            return Response("Only simple users can perform this action.", status=401, mimetype='application/json')
    else:
        return Response("User not authenticated.", status=401, mimetype='application/json')

# =================================================================================================================================
# ============================================================= A D M I N =========================================================
# ADMIN: ΕΙΣΑΓΩΓΗ ΠΡΟΪΟΝΤΟΣ =======================================================================================================
@app.route('/insertProduct', methods=['POST'])
def insert_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "productID" in data or not "name" in data or not "category" in data or not "quantity" in data or not "description" in data or not "price" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    if flag:
        currUser = users.find_one({'email':data["email"]})
        flag2 = currUser.get('category')
        if flag2=="Admin":
            #store the product in the product dictionary
            product = {"productID" : data['productID'], "name": data['name'], "category": data['category'], "quantity":data['quantity'], "description":data['description'], "price":data['price']}
            #inserting them in Products collection
            products.insert_one(product)
            #response
            return Response(data['name'] + " was added to the MongoDB", status=200, mimetype='application/json')
        else:
            return Response("Only admins can perform this action.", status=401, mimetype='application/json')
    else:
        return Response("Admin not authenticated.", status=401, mimetype='application/json')

# ADMIN: ΔΙΑΓΡΑΦΗ ΠΡΟΪΟΝΤΟΣ =======================================================================================================
@app.route('/deleteProduct', methods=['DELETE'])
def delete_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "productID" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    if flag:
        currUser = users.find_one({'email':data["email"]})
        flag2 = currUser.get('category')
        if flag2=="Admin":
            #Finding the product through its id and putting the result to dictionary product 
            product = products.find_one({"productID":data['productID']})
            #Checking if the product with the given id exists
            if product != None:
                #Deleting the product from the collection
                products.delete_one(product)
                #Passing the product's name and the string " was deleted" to variable msg
                msg = product['name'] + " was deleted successfully"
                #Response if query executed successfully
                return Response(msg, status=200, mimetype='application/json')
            #There is no student with the given email
            else:
                #Response if there is no product with the given id
                return Response("No product with that id was found", status=500, mimetype='application/json')
        else:
            return Response("Only admins can perform this action.", status=401, mimetype='application/json')
    else:
        return Response("Admin not authenticated.", status=401, mimetype='application/json')

# ADMIN: ΕΝΗΜΕΡΩΣΗ ΠΡΟΪΟΝΤΟΣ ======================================================================================================
@app.route('/editProduct', methods=['PATCH'])
def edit_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "productID" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    if not "name" in data and not "price" in data and not "description" in data:
        return Response("Not enough information to make changes to a product.",status=500,mimetype="application/json")
    
    uuid = request.headers.get('authorization')
    flag = is_session_valid(uuid)

    if flag:
        currUser = users.find_one({'email':data["email"]})
        flag2 = currUser.get('category')
        if flag2=="Admin":
            #find product 
            product = products.find_one({"productID":data['productID']})

            if product != None:
                if "name" in data:
                    products.update_one({'productID':data["productID"]}, {'$set':{'name':data["name"]}})

                if "price" in data:
                    products.update_one({'productID':data["productID"]}, {'$set':{'price':data["price"]}})
                
                if "description" in data:
                    products.update_one({'productID':data["productID"]}, {'$set':{'description':data["description"]}})
                
                #Passing the product's name and the string " was edited successfully" to variable msg
                msg = product['name'] + " was edited successfully"
                return Response(msg, status=200, mimetype='application/json')
            # no product with given id
            else:
                return Response("No product with that id was found", status=500, mimetype='application/json')
        else:
            return Response("Only admins can perform this action.", status=401, mimetype='application/json')        
    else:
        return Response("Admin not authenticated.", status=401, mimetype='application/json')

# the functions below are not requested, but the helped see what was inside the users and products databases

# @app.route('/getAllUsers', methods=['GET'])
# def get_all_users():
#     iterable = users.find({})
#     output = []
#     for user in iterable:
#         user['_id'] = None
#         output.append(user)
#     return jsonify(output)

# @app.route('/getAllProducts', methods=['GET'])
# def get_all_products():
#     iterable = products.find({})
#     output = []
#     for product in iterable:
#         product['_id'] = None
#         output.append(product)
#     return jsonify(output)


# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)