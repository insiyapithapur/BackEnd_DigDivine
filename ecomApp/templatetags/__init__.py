from django import template
register = template.Library()
from ecomApp.models import *
from django.db.models import Sum

@register.simple_tag
def totalAmount(orderId):
    queryset = OrderProduct.objects.filter(order=orderId)
    totalAmt = sum(float(item.PricePerPiece) for item in queryset)
    return round(totalAmt, 2)

@register.simple_tag
def totalDiscount(orderId):
    queryset = OrderProduct.objects.filter(order=orderId)
    totalAmt = sum((float(item.PricePerPiece) * item.productQty ) for item in queryset)
    discountedPrice = sum(float(item.DiscountPerPiece) for item in queryset)
    totalDiscountAmt = sum((float(item.DiscountPerPiece) * item.productQty) for item in queryset)
    totalPV = sum(float(item.product.personalVolume) for item in queryset)
    totalBV = sum(float(item.product.businessVolume) for item in queryset)
    totalItem = sum(int(item.productQty) for item in queryset)
    return {
        "discountSum":discountedPrice,
        "totalDiscount": totalAmt-totalDiscountAmt, 
        "totalPayble":totalDiscountAmt,
        "totalPv":totalPV, 
        "totalBv":totalBV,
        "totalQty":totalItem
        }
