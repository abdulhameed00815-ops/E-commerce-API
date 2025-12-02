const confirmCheckout = document.getElementById('confirm-checkout');

confirmCheckout.addEventListener('click', () => { 
	const token = localStorage.getItem('access_token');
	const cartId = localStorage.getItem('cart_id');
	
	fetch(`/viewcart/${cartId}`, {
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
	
			fetch('the_name_of_the_route', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(items)
			})
			.then((res) => {
				if (res.ok) return res.json()
			})
			.then(({ url}) => {
				window.location = url
			})
})
	
