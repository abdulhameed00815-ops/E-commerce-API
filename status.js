const stripe = Stripe('pk_test_51SQPxa06yHxJPVTJ64OspbHQVl7JGgVM8Jn0Zn4KrFykmGMvT1fNUmeYujisRDXS3Pb3rRa8n20QBff7OL2P8mgs00NWoKxJf4');

const clientSecret = new URLSearchParams(window.location.search).get(
	'payment_intent_client_secret'
);

stripe.retrievePaymentIntent(clientSecret).then(({paymentIntent}) => {
	const message = document.querySelector('#message')

	switch (paymentIntent.status) {
		case 'succeeded':
			message.innerText = 'Success! Payment recieved.';
			break;

		case 'processing':
			message.innerText = "Payment processing. We 'll update you when payment is recieved.";
			break;

		case 'requires_payment_method':
			message.innerText = 'Payment failed. please try another payment method.';
			window.location.assign('http://localhost:5500/checkout.html');
			break;

		default:
			message.innerText = 'somthing went wrong.';
			break;
	}
});
