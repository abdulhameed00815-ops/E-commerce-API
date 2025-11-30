const stripe = Stripe('pk_test_51SQPxa06yHxJPVTJ64OspbHQVl7JGgVM8Jn0Zn4KrFykmGMvT1fNUmeYujisRDXS3Pb3rRa8n20QBff7OL2P8mgs00NWoKxJf4');

(async () => {
	const response = await fetch('http://127.0.0.1:8000/secret');
	const {client_secret: clientSecret} = await response.json();

	const options = {
	  clientSecret: clientSecret,
	};
	
	const elements = stripe.elements(options);

	const paymentElementOptions = { layout: 'accordion'};
	const paymentElement = elements.create('payment', paymentElementOptions);
	paymentElement.mount('#payment-element');

	const form = document.getElementById('payment-form');

	form.addEventListener('submit', async (event) => {
		event.preventDefault();

		const {error} = await stripe.confirmPayment({
			elements,
			confirmParams: {
				return_url: 'http://localhost:5500/post-checkout.html',
			},
		});

		if (error) {
			const messageContainer = document.querySelector('#error-message');
			messageContainer.textContent = error.message;
		} else {

		}
	});
})();

