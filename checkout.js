const confirmCheckout = document.getElementById('confirm-checkout');

confirmCheckout.addEventListener('click', () => { 
	const token = localStorage.getItem('access_token');
	const cartId = localStorage.getItem('cart_id');
	
	fetch(`http://127.0.0.1:8000/viewcart/${cartId}`, {
		method: 'GET',
		headers: {
			"Authorization": `Bearer ${token}`,
			"Accept": 'application/json, text/plain, */*',
			"Content-type": 'application/json'
		}

	})
  	.then(res => {
        	return res.json().then(data => ({ status: res.status, data: data }));
        })
        .then(({ status, data }) => {
        	if (status === 200) {
			const items = data.cart_products;
	
			fetch('http://127.0.0.1:8000/create_checkout_session', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(items)
			})
			.then((res) => {
				if (res.ok) return res.json()
				return res.json().then(json => Promise.reject(json))
			})
			.then(({ url }) => {
				window.location = url;
			})
			.catch((e) => {
				console.error(e)
			})
		}
	});
});
