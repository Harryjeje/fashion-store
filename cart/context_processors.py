from .cart import Cart

# create context processor so our cart can work on all pages
def cart(request):
	# Return the default data ffrom our cart
	return{'cart': Cart(request)}