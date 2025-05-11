def orders_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    orders = Order.objects.filter(musteri=request.user).order_by('-tarix')
    statistics = Order.get_order_statistics(request.user)
    
    return render(request, 'orders.html', {
        'orders': orders,
        'statistics': statistics
    })

def order_detail_view(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    order = get_object_or_404(Order, id=order_id, musteri=request.user)
    return render(request, 'order_detail.html', {
        'order': order
    }) 