from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Campaign, Donation
from .forms import DonationForm
from django.contrib import messages

@login_required(login_url='accounts:login')
def fundraising_list(request):
    campaigns = Campaign.objects.filter(is_active=True).order_by('-created_at')
    total_raised = Campaign.objects.aggregate(Sum('current_amount'))['current_amount__sum'] or 0
    total_donors = Donation.objects.filter(status='completed').values('donor').distinct().count()
    recent_donations = Donation.objects.filter(status='completed').order_by('-donated_at')[:5]
    
    context = {
        'campaigns': campaigns,
        'total_raised': total_raised,
        'total_donors': total_donors,
        'recent_donations': recent_donations,
    }
    return render(request, 'fundraising/list.html', context)

@login_required(login_url='accounts:login')
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    recent_donations = campaign.donations.filter(status='completed').order_of_donated_at = campaign.donations.filter(status='completed').order_by('-donated_at')[:5]
    form = DonationForm()
    
    context = {
        'campaign': campaign,
        'recent_donations': recent_donations,
        'form': form,
    }
    return render(request, 'fundraising/detail.html', context)

import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Initialize Razorpay Client inside a function to ensure settings are loaded
def get_razorpay_client():
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET

    if not key_id or not key_secret:
        raise ValueError("Razorpay keys are missing from the .env file.")
    
    if key_id == "your_key_id_here" or key_secret == "your_key_secret_here":
        raise ValueError("You are still using PLACEHOLDER keys in the .env file. Please replace 'your_key_id_here' and 'your_key_secret_here' with your real Razorpay keys.")
        
    return razorpay.Client(auth=(key_id, key_secret))

@login_required(login_url='accounts:login')
def initiate_donation(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            # Razorpay expects amount in paise (multiply by 100)
            amount_paise = int(amount * 100)
            
            try:
                client = get_razorpay_client()
                # 1. Create Order in Razorpay
                order_data = {
                    'amount': amount_paise,
                    'currency': 'INR',
                    'payment_capture': '1'
                }
                razorpay_order = client.order.create(data=order_data)
                
                # 2. Create pending Donation in DB
                donation = Donation.objects.create(
                    donor=request.user,
                    campaign=campaign,
                    amount=amount,
                    status='pending',
                    razorpay_order_id=razorpay_order['id']
                )
                
                # 3. Return order info to frontend
                response_data = {
                    'order_id': razorpay_order['id'],
                    'merchant_key': settings.RAZORPAY_KEY_ID,
                    'amount': amount_paise,
                    'currency': 'INR',
                    'campaign_title': campaign.title,
                    'user_name': request.user.full_name,
                    'user_email': request.user.email,
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
            
    return redirect('fundraising:detail', campaign_id=campaign.id)

@csrf_exempt
@login_required(login_url='accounts:login')
def verify_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 1. Verify Signature
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            client = get_razorpay_client()
            client.utility.verify_payment_signature(params_dict)
            
            # 2. Update Donation and Campaign progress
            with transaction.atomic():
                donation = get_object_or_404(Donation, razorpay_order_id=data['razorpay_order_id'])
                donation.razorpay_payment_id = data['razorpay_payment_id']
                donation.razorpay_signature = data['razorpay_signature']
                donation.status = 'completed'
                donation.save()
                
                # Update Campaign amount
                campaign = donation.campaign
                # Recalculate from all completed donations to be safe, or just increment
                # To avoid race conditions, we use an atomic increment if possible, 
                # but campaign.save() is already in a transaction here.
                campaign.current_amount += donation.amount
                campaign.save()
                
            messages.success(request, f"Payment Successful! Thank you for your contribution of ₹{donation.amount}")
            return JsonResponse({'status': 'success'})
            
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'error', 'message': 'Signature verification failed'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
