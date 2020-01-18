import stripe, datetime, plaid, os
from flask import Flask, jsonify, render_template, request, redirect, url_for


app = Flask(__name__)

stripe_keys = {
  'secret_key': 'sk_test_pxUuaANGXrRy7EIBgW2AzPFH',
  'publishable_key': 'pk_test_hWMwML4SxDuvVDqsg94BzyZc'
}

stripe.api_key = stripe_keys['secret_key']
# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID', '5c9803fa9a4dbe0013ab6fa1')
PLAID_SECRET = os.getenv('PLAID_SECRET', '9c5b8fd0346c6bbd28a8a1c6e10164')
PLAID_PUBLIC_KEY = os.getenv(
    'PLAID_PUBLIC_KEY', '876ac00102185596106c2c076d5223')
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')
client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')

@app.route('/card', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bank_usage = False
        first_name = request.form['first_name']
        last_name=request.form['last_name']
        email = request.form['email']
        country=request.form['country']
        full_phone=request.form['full_phone']
        phone=request.form['phone']
        describe=request.form['describe']
        cc_number=request.form['cc_number']
        cc_cvv=request.form['cc_cvv']
        cc_expire=request.form['cc_expire']
        # routing_number=request.form['routing_number']
        # acc_number=request.form['acc_number']
        # acc_number_confirm=request.form['acc_number_confirm']
        cc_number = cc_number.replace(" ","")
        cc_expire = cc_expire.replace(" ","")
        cc_expire_split = cc_expire.split("/")
        cc_expire_join = cc_expire.replace("/","")
        if not phone.isdigit():
            return render_template('main.html', phone_number_digit=True, error_valid=True)
        # if len(cc_number) > 0 or len(cc_expire_split[0]) > 0 or len(cc_cvv) == 4: 
        if "/" not in cc_expire:
            return render_template('main.html', demarcate_not_present=True, error_valid=True)
        if len(cc_expire_split[0]) != 2 or len(cc_expire_split[1]) != 2:
            return render_template('main.html', expire_wrong_format=True, error_valid=True)
        if not cc_number.isdigit():
            return render_template('main.html', cc_number_digit=True, error_valid=True)
        if len(cc_number) != 16:
            return render_template('main.html', cc_number_length=True, error_valid=True)
        if not cc_expire_join.isdigit():
            return render_template('main.html', cc_expire_digit=True, error_valid=True)
        if not cc_cvv.isdigit():
            return render_template('main.html', cc_cvv_digit=True, error_valid=True)
        if not (len(cc_cvv) == 3 or len(cc_cvv) == 4):
            return render_template('main.html', cc_cvv_length=True, error_valid=True)
        today = datetime.datetime.now().timetuple()
        time = datetime.datetime(today[0],today[1],today[2],today[3],today[4]).timestamp()
        account = stripe.Account.create(type="custom",country=country,tos_acceptance={"date":int(time), "ip":"127.0.0.1"},product_description=describe,email=email,legal_entity={"first_name":first_name,"last_name":last_name, "personal_email":email, "personal_phone_number":full_phone, "phone_number":full_phone},requested_capabilities=["card_payments", "transfers",],)
        try:
            token = stripe.Token.create(card={"number": cc_number,"exp_month": cc_expire_split[0],"exp_year": cc_expire_split[1],"currency":"usd", "cvc":cc_cvv},)            
            credit_card = stripe.Account.create_external_account(account["id"],external_account=token["id"])
        except:
            return render_template('main.html', not_debit_card=True, error_valid=True)
        account_links = stripe.AccountLink.create(account=account["id"],failure_url='https://afriex-stripe.herokuapp.com/failure',success_url='https://afriex-stripe.herokuapp.com/success',type='custom_account_verification',collect='currently_due',)
        # print([first_name, last_name, email, country, phone, full_phone, describe, cc_number, cc_expire, cc_cvv, routing_number, acc_number, acc_number_confirm]) 
        return redirect(account_links["url"])

        # bank_usage = True
        # if not routing_number.isdigit():
        #     return render_template('main.html', routing_number_digit=True, bank_usage=bank_usage, error_valid=True)
        # if len(routing_number) != 9:
        #     return render_template('main.html', routing_number_length=True, bank_usage=bank_usage, error_valid=True)
        # if acc_number != acc_number_confirm:
        #     return render_template('main.html', acc_number_unmatch=True, bank_usage=bank_usage, error_valid=True)
        # if not acc_number.isdigit():
        #     return render_template('main.html', acc_number_digit=True, bank_usage=bank_usage, error_valid=True)
        # if len(acc_number) != 12:
        #     return render_template('main.html', acc_number_length=True, bank_usage=bank_usage, error_valid=True)
        # today = datetime.datetime.now().timetuple()
        # time = datetime.datetime(today[0],today[1],today[2],today[3],today[4]).timestamp()
        # account = stripe.Account.create(type="custom",country=country,tos_acceptance={"date":int(time), "ip":"127.0.0.1"},product_description=describe,email=email,legal_entity={"first_name":first_name,"last_name":last_name, "personal_email":email, "personal_phone_number":full_phone, "phone_number":full_phone},requested_capabilities=["card_payments", "transfers",],)
        # try:
        #     token = stripe.Token.create(bank_account={"country": country,"currency": "usd","routing_number": routing_number,"account_number": acc_number,},)        
        #     bank = stripe.Account.create_external_account(account["id"],external_account=token["id"])
        # except:
        #     return render_template('main.html', not_bank_account=True, bank_usage=bank_usage, error_valid=True)
        # account_links = stripe.AccountLink.create(account=account["id"],failure_url='https://afriex-stripe.herokuapp.com/failure',success_url='https://afriex-stripe.herokuapp.com/success',type='custom_account_verification',collect='currently_due',)
        # return redirect(account_links["url"])        
    return render_template('main.html')

@app.route('/get_bank_info', methods=['POST'])
def get_bank_info():
    PLAID_LINK_PUBLIC_TOKEN = request.form['public_token']
    ACCOUNT_ID = request.form['account_id']
    exchange_token_response = client.Item.public_token.exchange(PLAID_LINK_PUBLIC_TOKEN)

    access_token = exchange_token_response['access_token']
    print(access_token)

    stripe_response = client.Processor.stripeBankAccountTokenCreate(
        access_token, ACCOUNT_ID)
    bank_account_token = stripe_response['stripe_bank_account_token']
    print(bank_account_token)
    today = datetime.datetime.now().timetuple()
    time = datetime.datetime(today[0],today[1],today[2],today[3],today[4]).timestamp()
    account = stripe.Account.create(type="custom",country='us',tos_acceptance={"date":int(time), "ip":"127.0.0.1"},requested_capabilities=["card_payments", "transfers",],)
    try:
        bank = stripe.Account.create_external_account(account["id"],external_account=bank_account_token)
    except:
        return jsonify({'error': "cannot create external account"})        
        # return render_template('main.html', not_bank_account=True, bank_usage=bank_usage, error_valid=True)
    account_links = stripe.AccountLink.create(account=account["id"],failure_url='https://afriex-stripe.herokuapp.com/failure',success_url='https://afriex-stripe.herokuapp.com/success',type='custom_account_verification',collect='currently_due',)
    # return redirect(account_links["url"])
    return jsonify({'redirect': account_links["url"]})
    # return redirect(url_for("success"))

@app.route('/success')
def success():
    previous_url = request.referrer
    print(previous_url)
    if previous_url == None:
        return redirect(url_for("testt"))
    return render_template('success.html')

@app.route('/failure')
def failure():
    previous_url = request.referrer
    print(previous_url)
    if previous_url == None:
        return redirect(url_for("testt"))
    return render_template('failure.html')


@app.route('/')
def testt():
    return render_template("index.html", PLAID_PUBLIC_KEY=PLAID_PUBLIC_KEY)


if __name__ == '__main__':
    app.run(debug=True)
