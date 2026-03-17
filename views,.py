
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render, redirect,get_object_or_404
# from django.http import JsonResponse
# from authentication.models import CustomUser
# from waste_collector_dashboard.models import WasteCollection
# # from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate  # Moved inside functions to avoid circular import
# from django.contrib import messages
# from .utils import is_super_admin
# from django.template.loader import get_template, render_to_string
# from django.utils import timezone
# from django.db.models import Sum
# from datetime import datetime
# from .models import State, District, LocalBody, LocalBodyCalendar, CollectorServiceArea

# def get_ward_names():
#     """Return a dictionary mapping ward numbers to ward names"""
#     return {
#         1: "Fort Kochi",
#         2: "Kalvathy",
#         3: "Earavely",
#         4: "Karippalam",
#         5: "Cheralayi",
#         6: "Mattanchery",
#         7: "Chakkamadam",
#         8: "Karuvelippady",
#         9: "Island North",
#         10: "Ravipuram",
#         11: "Ernakulam South",
#         12: "Gandhi Nagar",
#         13: "Kathrikadavu",
#         14: "Ernakulam Central",
#         15: "Ernakulam North",
#         16: "Kaloor South",
#         17: "Kaloor North",
#         18: "Thrikkanarvattom",
#         19: "Ayyappankavu",
#         20: "Pottakuzhy",
#         21: "Elamakkara South",
#         22: "Pachalam",
#         23: "Thattazham",
#         24: "Vaduthala West",
#         25: "Vaduthala East",
#         26: "Elamakkara North",
#         27: "Puthukkalavattam",
#         28: "Kunnumpuram",
#         29: "Ponekkara",
#         30: "Edappally",
#         31: "Changampuzha",
#         32: "Dhevankulangara",
#         33: "Palarivattom",
#         34: "Stadium",
#         35: "Karanakkodam",
#         36: "Puthiyaroad",
#         37: "Padivattam",
#         38: "Vennala",
#         39: "Chakkaraparambu",
#         40: "Chalikkavattam",
#         41: "Thammanam",
#         42: "Elamkulam",
#         43: "Girinagar",
#         44: "Ponnurunni",
#         45: "Ponnurunni East",
#         46: "Vyttila",
#         47: "Poonithura",
#         48: "Vyttila Janatha",
#         49: "Kadavanthra",
#         50: "Panampilly Nagar",
#         51: "Perumanoor",
#         52: "Konthuruthy",
#         53: "Thevara",
#         54: "Island South",
#         55: "Kadebhagam",
#         56: "Palluruthy East",
#         57: "Thazhuppu",
#         58: "Eadakochi North",
#         59: "Edakochi South",
#         60: "Perumbadappu",
#         61: "Konam",
#         62: "Palluruthy Kacheripady",
#         63: "Nambyapuram",
#         64: "Palluruthy",
#         65: "Pullardesam",
#         66: "Tharebhagam",
#         67: "Thoppumpady",
#         68: "Mundamvely East",
#         69: "Mundamvely",
#         70: "Manassery",
#         71: "Moolamkuzhy",
#         72: "Chullickal",
#         73: "Nasrathu",
#         74: "Panayappilly",
#         75: "Amaravathy",
#         76: "Fortkochi Veli"
#     }

# def get_ward_options(localbody_name=None):
#     """Kochi/Ernakulam → 76 named wards (Fort Kochi, etc.); other local bodies → Ward 1 to Ward 10."""
#     ward_names = get_ward_names()
#     name_lower = (localbody_name or '').lower()
#     if name_lower and ('kochi' in name_lower or 'ernakulam' in name_lower):
#         return [(i, ward_names.get(i, f'Ward {i}')) for i in range(1, 77)]
#     return [(i, f'Ward {i}') for i in range(1, 11)]


# @login_required
# def admin_home(request):
#     from customer_dashboard.models import CustomerPickupDate, CustomerWasteInfo
#     from django.db.models import Count, Q

#     # Get current date info
#     now = timezone.now()
#     first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

#     # Calculate statistics
#     total_customers = CustomUser.objects.filter(role=0).count()
#     total_collectors = CustomUser.objects.filter(role=1).count()

#     # Collections this month
#     monthly_collections = WasteCollection.objects.filter(
#         created_at__gte=first_day_of_month
#     ).count()

#     # Total waste collected (sum of kg)
#     total_waste_collected_data = WasteCollection.objects.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     # 1. Collection Rate: Collections vs Scheduled Pickups
#     scheduled_pickups = CustomerPickupDate.objects.filter(
#         localbody_calendar__date__gte=first_day_of_month.date(),
#         localbody_calendar__date__lte=now.date()
#     ).count()

#     collection_rate = 0
#     if scheduled_pickups > 0:
#         collection_rate = min(100, int((monthly_collections / scheduled_pickups) * 100))
#     elif monthly_collections > 0:
#         collection_rate = 100

#     # 2. Customer Satisfaction: Based on "On-Time" collections
#     # If scheduled_date == collection_date or matches within 1 day
#     on_time_collections = 0
#     total_with_schedule = 0
#     collections_with_schedule = WasteCollection.objects.filter(
#         scheduled_date__isnull=False,
#         created_at__gte=first_day_of_month
#     )

#     for coll in collections_with_schedule:
#         total_with_schedule += 1
#         # Compare created_at date with scheduled_date
#         collection_date = coll.created_at.date()
#         scheduled_date = coll.scheduled_date

#         # Ensure we are comparing date to date (scheduled_date might be datetime in some cases)
#         if hasattr(scheduled_date, 'date'):
#             scheduled_date = scheduled_date.date()

#         if collection_date <= scheduled_date:
#             on_time_collections += 1

#     customer_satisfaction = 4.5 # Default high starting point
#     if total_with_schedule > 0:
#         satisfaction_ratio = on_time_collections / total_with_schedule
#         customer_satisfaction = round(3.0 + (satisfaction_ratio * 2.0), 1) # Scale between 3.0 and 5.0

#     # 3. Recycling Rate: Estimated based on waste types
#     # Check CustomerWasteInfo for recyclable types
#     recyclable_keywords = ['plastic', 'paper', 'metal', 'glass', 'can', 'bottle', 'recyclable']
#     recyclable_query = Q()
#     for kw in recyclable_keywords:
#         recyclable_query |= Q(waste_type__icontains=kw)

#     total_profiles = CustomerWasteInfo.objects.count()
#     recyclable_profiles = CustomerWasteInfo.objects.filter(recyclable_query).count()

#     recycling_rate = 0
#     if total_profiles > 0:
#         recycling_rate = int((recyclable_profiles / total_profiles) * 100)
#     else:
#         recycling_rate = 65 # Reasonable industry average placeholder if no data

#     # Get order data for control all orders functionality
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'user', 'state', 'district', 'localbody', 'assigned_collector'
#     ).all()

#     total_orders = waste_infos.count()
#     pending_orders = waste_infos.filter(status='pending').count()
#     confirmed_orders = waste_infos.filter(status='in_progress').count()
#     completed_orders = waste_infos.filter(status='completed').count()

#     # Get all collectors for dropdown
#     collectors = CustomUser.objects.filter(role=1)

#     # Build orders data from real CustomerWasteInfo
#     orders = []
#     for info in waste_infos[:20]:  # Limit to first 20 orders
#         try:
#             # Get scheduled date for this waste info
#             pickup_date = info.customerpickupdate_set.select_related('localbody_calendar').first()
#             scheduled_date_order = pickup_date.localbody_calendar.date.strftime('%Y-%m-%d') if pickup_date and pickup_date.localbody_calendar else 'Not Scheduled'

#             # Get assigned collector name
#             collector_name = info.assigned_collector.get_full_name() if info.assigned_collector else 'Unassigned'

#             # Convert status to readable format
#             status_map = {
#                 'pending': 'Pending',
#                 'in_progress': 'In Progress',
#                 'completed': 'Completed',
#                 'collected': 'Collected'
#             }
#             readable_status = status_map.get(info.status, info.status)

#             order = {
#                 'id': info.id,
#                 'customer_name': info.full_name,
#                 'customer_phone': info.user.contact_number,
#                 'address': info.pickup_address,
#                 'waste_type': info.waste_type,
#                 'bags': info.number_of_bags or 0,
#                 'booking_date': info.created_at.strftime('%Y-%m-%d'),
#                 'scheduled_date': scheduled_date_order,
#                 'status': readable_status,
#                 'assigned_collector': collector_name,
#                 'ward': info.ward,
#                 'localbody': info.localbody.name if info.localbody else 'Not Assigned'
#             }
#             orders.append(order)
#         except Exception as e:
#             print(f"Error processing order {info.id}: {e}")
#             continue

#     context = {
#         'total_customers': total_customers,
#         'total_collectors': total_collectors,
#         'monthly_collections': monthly_collections,
#         'total_waste_collected': f"{total_waste_collected_data:.1f} KG",
#         'collection_rate': collection_rate,
#         'customer_satisfaction': customer_satisfaction,
#         'recycling_rate': recycling_rate,
#         'orders': orders,
#         'total_orders': total_orders,
#         'pending_orders': pending_orders,
#         'confirmed_orders': confirmed_orders,
#         'completed_orders': completed_orders,
#         'collectors': collectors
#     }

#     return render(request, 'super_admin_dashboard.html', context)


# @login_required
# def manage_order(request, order_id):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     # Add logging for debugging
#     print(f"manage_order called with order_id: {order_id}, method: {request.method}")
#     print(f"User authenticated: {request.user.is_authenticated}")
#     print(f"User: {request.user}")

#     if request.method == 'POST':
#         try:
#             action = request.POST.get('action')
#             print(f"Action: {action}")

#             # Get the waste info object
#             waste_info = CustomerWasteInfo.objects.get(id=order_id)
#             print(f"Waste info found: {waste_info.id}")

#             # Handle order management actions
#             if action == 'assign_collector':
#                 collector_id = request.POST.get('collector_id')
#                 print(f"Assigning collector: {collector_id}")
#                 if collector_id:
#                     collector = CustomUser.objects.get(id=collector_id, role=1)  # role=1 for collectors
#                     waste_info.assigned_collector = collector
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} assigned to collector successfully')
#                     print("Collector assigned successfully")

#             elif action == 'update_status':
#                 new_status = request.POST.get('status')
#                 print(f"Updating status to: {new_status}")
#                 if new_status in ['pending', 'in_progress', 'completed', 'collected']:
#                     waste_info.status = new_status
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} status updated to {new_status}')
#                     print("Status updated successfully")

#             elif action == 'reschedule':
#                 new_date = request.POST.get('new_date')
#                 print(f"Rescheduling to: {new_date}")
#                 if new_date:
#                     # First get or create the calendar entry if it doesn't exist
#                     calendar_entry, created = LocalBodyCalendar.objects.get_or_create(
#                         localbody=waste_info.localbody,
#                         date=new_date
#                     )
#                     # Update the scheduled date by creating/updating the CustomerPickupDate
#                     pickup_date, created = CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={'localbody_calendar': calendar_entry}
#                     )
#                     messages.success(request, f'Order {order_id} rescheduled to {new_date}')
#                     print("Order rescheduled successfully")

#             response_data = {'success': True}
#             print("Returning success response:", response_data)
#             return JsonResponse(response_data)

#         except CustomerWasteInfo.DoesNotExist:
#             error_msg = f'Order {order_id} not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except CustomUser.DoesNotExist:
#             error_msg = 'Collector not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except LocalBodyCalendar.DoesNotExist:
#             error_msg = 'Schedule date not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except Exception as e:
#             error_msg = str(e)
#             print("Unexpected error:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     # If not POST method
#     error_msg = 'Invalid request method'
#     print("Error:", error_msg)
#     return JsonResponse({'success': False, 'error': error_msg}, status=405)


# @login_required
# def user_list_view(request):
#     customers = CustomUser.objects.filter(role=0)
#     collectors = CustomUser.objects.filter(role=1)
#     admins = CustomUser.objects.filter(role=2)

#     return render(request, 'user_list.html', {
#         'customers': customers,
#         'collectors': collectors,
#         'admins': admins,
#     })
# @login_required
# def view_customers(request):
#     customers = CustomUser.objects.filter(role=0)
#     return render(request, 'view_customers.html', {'customers': customers})

# @login_required
# def view_waste_collectors(request):
#     collectors = CustomUser.objects.filter(role=1)
#     total_collectors = collectors.count()
#     service_areas = CollectorServiceArea.objects.select_related(
#         'collector', 'district', 'localbody'
#     ).order_by('collector__username', 'district__name', 'localbody__name')
#     # Same as view_collected_data: all districts and localbodies for dropdowns
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')
#     # Ward dropdown: use dedicated collectors endpoint (same app, login only)
#     from django.urls import reverse
#     try:
#         load_wards_url = request.build_absolute_uri(
#             reverse('adminpanel:load_wards_collectors', args=[0])
#         ).replace('/0/', '/')
#     except Exception:
#         load_wards_url = request.build_absolute_uri('/admin/users/collectors/load-wards/')
#     return render(request, 'view_collectors.html', {
#         'collectors': collectors,
#         'total_collectors': total_collectors,
#         'service_areas': service_areas,
#         'districts': districts,
#         'localbodies': localbodies,
#         'load_wards_url': load_wards_url,
#     })


# @login_required
# def assign_collector_service_area(request):
#     """Assign a service area (District, Local Body, Ward) to a waste collector."""
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
#     collector_id = request.POST.get('collector_id')
#     district_id = request.POST.get('district_id')
#     localbody_id = request.POST.get('localbody_id')
#     ward = request.POST.get('ward', '').strip()
#     if not all([collector_id, district_id, localbody_id, ward]):
#         return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
#     collector = get_object_or_404(CustomUser, id=collector_id, role=1)
#     district = get_object_or_404(District, id=district_id)
#     localbody = get_object_or_404(LocalBody, id=localbody_id)
#     if localbody.district_id != district.id:
#         return JsonResponse({'success': False, 'error': 'Local body does not belong to selected district'}, status=400)
#     obj, created = CollectorServiceArea.objects.get_or_create(
#         collector=collector,
#         district=district,
#         localbody=localbody,
#         ward=ward,
#     )
#     if created:
#         messages.success(request, f'Service area {district.name} / {localbody.name} / {ward} assigned to {collector.username}')
#     else:
#         messages.info(request, 'This service area is already assigned to this collector')
#     return redirect('adminpanel:view_collectors')


# @login_required
# def remove_collector_service_area(request, pk):
#     """Remove a service area assignment from a collector."""
#     if request.method != 'POST':
#         return redirect('adminpanel:view_collectors')
#     area = get_object_or_404(CollectorServiceArea, pk=pk)
#     area.delete()
#     messages.success(request, 'Service area assignment removed')
#     return redirect('adminpanel:view_collectors')


# @login_required
# def load_wards_collectors(request, localbody_id):
#     """Load wards for view_collectors and price_control - only requires login"""
#     try:
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name or "")
#         wards_data = [
#             {"ward_number": str(option[0]), "ward_name": option[1] or f"Ward {option[0]}"}
#             for option in ward_options
#         ]
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse([], safe=False)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# def load_localbodies_collectors(request, district_id):
#     """Load local bodies for view_collectors and price_control - only requires login"""
#     try:
#         lbs = LocalBody.objects.filter(district_id=district_id).order_by('name')
#         data = [
#             {"id": lb.id, "name": lb.name or "", "body_type": lb.body_type or "", "body_type_display": lb.get_body_type_display()}
#             for lb in lbs
#         ]
#         return JsonResponse(data, safe=False)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# def view_super_admin(request):
#     super_admin = CustomUser.objects.filter(role=2)
#     return render(request, "view_super_admin.html", {"super_admin":super_admin})

# @login_required
# def view_admins(request):
#     admins = CustomUser.objects.filter(role=3)
#     return render(request, "view_admins.html", {"admins":admins})

# # \\\\\\\\\\\\\\\\\\\\\\\\\\\ user view //////////////////////

# from .forms import UserForm

# @login_required
# def user_list(request):
#     users = CustomUser.objects.all()
#     return render(request, "users_list.html", {"users": users})





# @login_required
# def user_create(request):
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Encrypt password before saving
#                 user.set_password(password)
#             else:  # Default password if none provided
#                 user.set_password("default123")
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm()
#     return render(request, 'user_form.html', {'form': form})

# # Update User
# @login_required
# def user_update(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == 'POST':
#         form = UserForm(request.POST, instance=user)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Reset password if admin entered new one
#                 user.set_password(password)
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm(instance=user)
#     return render(request, 'user_form.html', {'form': form, 'user': user})






# # Delete user
# @login_required
# def user_delete(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         user.delete()
#         messages.success(request, "User deleted successfully")
#         return redirect("super_admin_dashboard:users_list")
#     return render(request, "user_confirm_delete.html", {"user": user})



# from django.shortcuts import render
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser

# @login_required
# def view_customer_wasteinfo(request):
#     # Fetch only unassigned customer waste profiles with related fields
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'state', 'district', 'localbody', 'assigned_collector', 'user'
#     ).filter(assigned_collector__isnull=True)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     # Map waste_info_id → pickup date
#     pickup_dates = {}
#     pickups = CustomerPickupDate.objects.select_related('localbody_calendar', 'waste_info').all()
#     for pickup in pickups:
#         if pickup.waste_info:
#             pickup_dates[pickup.waste_info.id] = pickup.localbody_calendar.date

#     return render(request, 'view_customer_wasteinfo.html', {
#         'waste_infos': waste_infos,
#         'collectors': collectors,
#         'pickup_dates': pickup_dates,
#     })

# # Assign a waste collector to a CustomerWasteInfo entry
# @login_required
# def assign_waste_collector(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)
#     if request.method == 'POST':
#         collector_id = request.POST.get('collector')
#         collector = get_object_or_404(CustomUser, pk=collector_id, role=1)

#         # Store customer info for success message
#         customer_name = waste_info.user.username
#         customer_address = waste_info.pickup_address

#         # Assign collector and ensure is_collected is False so it appears in assigned customers list
#         waste_info.assigned_collector = collector
#         waste_info.is_collected = False  # Mark as not collected so collector can see it
#         waste_info.save()

#         messages.success(request, f"Customer {customer_name} at {customer_address} has been assigned to {collector.username}. The customer now appears in the collector's assigned customers list.")
#         return redirect('super_admin_dashboard:view_customer_waste_info')

#     collectors = CustomUser.objects.filter(role=1)
#     return render(request, 'assign_waste_collector.html', {
#         'waste_info': waste_info,
#         'collectors': collectors,
#     })


# #waste collector collect details from customer

# def can_view_collected_data(user):
#     # Role 1 is Collector, Role 2 is Super Admin
#     return user.is_authenticated and (getattr(user, 'role', None) in [1, 2] or user.is_superuser)

# @login_required
# @user_passes_test(can_view_collected_data)
# def view_collected_data(request):
#     # Get waste collection data with related information
#     user_role = getattr(request.user, 'role', None)
#     try:
#         user_role = int(user_role)
#     except (TypeError, ValueError):
#         user_role = None

#     # Get filter parameters
#     district_filter = request.GET.get('district')
#     localbody_filter = request.GET.get('localbody')
#     phone_filter = request.GET.get('phone')
#     from_date_filter = request.GET.get('from_date')
#     to_date_filter = request.GET.get('to_date')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {District.objects.count()}")
#     print(f"DEBUG: LocalBodies count: {LocalBody.objects.count()}")
#     print(f"DEBUG: Selected filters - District: {district_filter}, LocalBody: {localbody_filter}, Phone: {phone_filter}")

#     # Base queryset
#     if user_role == 1:
#         # Collector (Role 1) sees only their own data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).filter(collector=request.user)
#     else:
#         # Admin (Role 2) or others see all data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).all()

#     # Apply filters
#     if district_filter:
#         all_data = all_data.filter(localbody__district__id=district_filter)

#     if localbody_filter:
#         all_data = all_data.filter(localbody__id=localbody_filter)

#     if phone_filter:
#         all_data = all_data.filter(
#             Q(customer__contact_number__icontains=phone_filter) |
#             Q(collector__contact_number__icontains=phone_filter)
#         )

#     if from_date_filter:
#         try:
#             from_date = datetime.strptime(from_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__gte=from_date)
#         except ValueError:
#             pass

#     if to_date_filter:
#         try:
#             to_date = datetime.strptime(to_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__lte=to_date)
#         except ValueError:
#             pass

#     # Filter by month if requested (legacy functionality)
#     month_filter = request.GET.get('month')
#     if month_filter == 'current':
#         from django.utils import timezone
#         now = timezone.now()
#         first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         all_data = all_data.filter(created_at__gte=first_day_of_month)

#     # Order by created_at descending
#     all_data = all_data.order_by('-created_at')

#     # Get districts and localbodies for filter dropdowns
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Final districts count: {districts.count()}")
#     print(f"DEBUG: Final localbodies count: {localbodies.count()}")
#     print(f"DEBUG: Filtered data count: {all_data.count()}")

#     # Handle AJAX request for filtered data
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         # Prepare data for JSON response
#         data = []
#         for item in all_data:
#             data.append({
#                 'id': item.id,
#                 'collector': item.collector.username,
#                 'customer': item.customer.username,
#                 'localbody': item.localbody.name if item.localbody else 'Not assigned',
#                 'ward': item.ward,
#                 'location': item.location,
#                 'number_of_bags': item.number_of_bags,
#                 'building_no': item.building_no,
#                 'street_name': item.street_name,
#                 'kg': float(item.kg),
#                 'total_amount': float(item.total_amount) if item.total_amount else 0,
#                 'payment_method': item.get_payment_method_display(),
#                 'photo_url': item.photo.url if item.photo else None,
#                 'booking_date': item.booking_date.strftime('%Y-%m-%d %H:%M') if item.booking_date else '',
#                 'collection_time': item.collection_time.strftime('%H:%M') if item.collection_time else '',
#                 'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                 'scheduled_date': item.scheduled_date.strftime('%Y-%m-%d') if item.scheduled_date else '',
#             })

#         return JsonResponse({
#             'data': data,
#             'total_count': len(data)
#         })

#     return render(request, 'view_collected_data.html', {
#         'all_data': all_data,
#         'districts': districts,
#         'localbodies': localbodies,
#         'selected_district': district_filter,
#         'selected_localbody': localbody_filter,
#         'selected_phone': phone_filter,
#         'selected_from_date': from_date_filter,
#         'selected_to_date': to_date_filter,
#         'all_data': all_data
#     })


# # ////// MAP_ROLE
# @login_required
# def map_role(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         new_role = request.POST.get("role")
#         if new_role is not None:
#             try:
#                 new_role = int(new_role)  # Convert string to int
#                 if new_role in dict(CustomUser.ROLE_CHOICES).keys():
#                     user.role = new_role
#                     user.save()
#                     return redirect("super_admin_dashboard:users_list")
#             except ValueError:
#                 pass  # Ignore invalid input
#     return render(request, "map_role.html", {"user": user, "roles": CustomUser.ROLE_CHOICES})







# # ////////////////////////////      CALENDAR SET UP     ///////////////////////////////////


# import json
# from datetime import date, datetime, timedelta

# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
# from django.views.decorators.http import require_POST, require_GET
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.utils.dateparse import parse_date
# from django.template.loader import get_template


# from .models import State, District, LocalBody, LocalBodyCalendar
# from .utils import is_super_admin





# @login_required
# @user_passes_test(is_super_admin)
# def calendar_view(request):
#     """Main page where admin picks state/district/localbody and sees FullCalendar."""
#     states = State.objects.all().order_by("name")
#     return render(request, "calendar.html", {"states": states})


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_districts(request, state_id):
#     districts = District.objects.filter(state_id=state_id).values("id", "name")
#     return JsonResponse(list(districts), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_localbodies(request, district_id):
#     lbs = LocalBody.objects.filter(district_id=district_id).values("id", "name", "body_type")
#     return JsonResponse(list(lbs), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_wards(request, localbody_id):
#     """Load wards for a specific localbody"""
#     try:
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         # Convert to the format expected by the frontend
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# # Test endpoint without authentication for debugging
# def debug_wards_no_auth(request, localbody_id):
#     """Debug endpoint to test ward loading without authentication"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         print(f"DEBUG NO AUTH: Loading wards for localbody_id {localbody_id}")
#         print(f"DEBUG NO AUTH: Found {len(wards_data)} wards")
#         print(f"DEBUG NO AUTH: Sample data: {wards_data[:2] if wards_data else 'None'}")
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         print(f"DEBUG NO AUTH: Error: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates(request, localbody_id):
#     events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#     # FullCalendar expects events with at least id and start
#     data = [{"id": e["id"], "title": "Assigned", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates_by_ward(request, localbody_id):
#     """Get calendar dates filtered by ward number"""
#     ward_number = request.GET.get('ward')
#     if ward_number:
#         # For now, we'll return all calendar dates for the localbody
#         # In a more advanced implementation, you might have ward-specific calendar entries
#         events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#         data = [{"id": e["id"], "title": f"Assigned - Ward {ward_number}", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     else:
#         data = []
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def create_calendar_date(request, localbody_id):
#     """Create one date or range. Expects 'date' in YYYY-MM-DD or 'start' & 'end' for ranges."""
#     lb = get_object_or_404(LocalBody, pk=localbody_id)

#     # support single-date or start/end
#     start = request.POST.get("start")
#     end = request.POST.get("end")
#     single = request.POST.get("date")

#     created = []
#     if single:
#         d = parse_date(single)
#         if not d:
#             return HttpResponseBadRequest("Invalid date")
#         entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=d)
#         if created_flag:
#             created.append({"id": entry.id, "date": entry.date.isoformat()})
#         return JsonResponse({"status": "created", "created": created})

#     if start and end:
#         s = parse_date(start)
#         e = parse_date(end)
#         if not s or not e:
#             return HttpResponseBadRequest("Invalid start/end")
#         cur = s
#         while cur <= e:
#             entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=cur)
#             if created_flag:
#                 created.append({"id": entry.id, "date": entry.date.isoformat()})
#             cur += timedelta(days=1)
#         return JsonResponse({"status": "created_range", "created": created})

#     return HttpResponseBadRequest("Provide 'date' or 'start' and 'end'.")


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def update_calendar_date(request, pk):
#     """Change date for an existing LocalBodyCalendar entry. Expect 'new_date' YYYY-MM-DD"""
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     new_date_raw = request.POST.get("new_date")
#     if not new_date_raw:
#         return HttpResponseBadRequest("Missing new_date")
#     new_date = parse_date(new_date_raw.split("T")[0])
#     if not new_date:
#         return HttpResponseBadRequest("Invalid date")
#     # prevent duplicates: if another entry exists for that localbody on same date -> reject
#     exists = LocalBodyCalendar.objects.filter(localbody=entry.localbody, date=new_date).exclude(pk=entry.pk).exists()
#     if exists:
#         return JsonResponse({"status": "conflict", "message": "Date already assigned"}, status=409)
#     entry.date = new_date
#     entry.save()
#     return JsonResponse({"status": "updated", "id": entry.id, "date": entry.date.isoformat()})


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def delete_calendar_date(request, pk):
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     entry.delete()
#     return JsonResponse({"status": "deleted", "id": pk})






# # /////////////// super admin create waste oder


# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser
# from super_admin_dashboard.models import State, District, LocalBody
# @login_required
# def create_waste_profile(request):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     if request.method == "POST":
#         contact_number = request.POST.get("contact_number")

#         # Step 1: Check if customer exists
#         try:
#             customer = CustomUser.objects.get(contact_number=contact_number, role=0)
#         except CustomUser.DoesNotExist:
#             messages.error(request, "No registered customer found with this contact number.")
#             return redirect("super_admin_dashboard:create_waste_profile")

#         # Step 2: Collect waste info details from form
#         full_name = request.POST.get("full_name")
#         secondary_number = request.POST.get("secondary_number")
#         pickup_address = request.POST.get("pickup_address")
#         landmark = request.POST.get("landmark")
#         pincode = request.POST.get("pincode")
#         state_id = request.POST.get("state")
#         district_id = request.POST.get("district")
#         localbody_id = request.POST.get("localbody")
#         waste_type = request.POST.get("waste_type")
#         number_of_bags = request.POST.get("number_of_bags")
#         ward = request.POST.get("ward")
#         selected_date_id = request.POST.get("selected_date")  # calendar selected date

#         # Step 3: Create Waste Profile
#         waste_info = CustomerWasteInfo.objects.create(
#             user=customer,
#             full_name=full_name,
#             secondary_number=secondary_number,
#             pickup_address=pickup_address,
#             landmark=landmark,
#             pincode=pincode,
#             state_id=state_id,
#             district_id=district_id,
#             localbody_id=localbody_id,
#             waste_type=waste_type,
#             number_of_bags=number_of_bags,
#             ward=ward
#         )

#         # Step 4: Save pickup date if given
#         if selected_date_id:
#             try:
#                 cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                 CustomerPickupDate.objects.create(
#                     user=customer,
#                     waste_info=waste_info,
#                     localbody_calendar=cal
#                 )
#             except LocalBodyCalendar.DoesNotExist:
#                 messages.warning(request, "Invalid pickup date selected.")

#         messages.success(request, f"Waste profile created for {customer.first_name}")
#         return redirect("super_admin_dashboard:view_customer_waste_info")

#     # GET request
#     states = State.objects.all()
#     ward_range = range(1, 74)  # Wards 1–73
#     bag_range = range(1, 11)   # Bags 1–10
#     # For super admin form, we don't have a localbody selected yet, so show numbers only
#     ward_options = get_ward_options(None)

#     return render(request, "superadmin_waste_form.html", {
#         "states": states,
#         "ward_range": ward_range,
#         "bag_range": bag_range,
#         "ward_options": ward_options,
#     })




# from .forms import WasteProfileForm  # we'll create this form



# @login_required
# def view_waste_profile(request, pk):
#     waste_info = get_object_or_404(
#         CustomerWasteInfo.objects.select_related(
#             "user", "state", "district", "localbody", "assigned_collector"
#         ),
#         pk=pk
#     )

#     # pickup dates for this profile
#     pickup_dates = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     return render(request, "superadmin_view_waste.html", {
#         "info": waste_info,
#         "pickup_dates": pickup_dates,
#     })



# @login_required
# def edit_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     existing_pickups = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     if request.method == "POST":
#         form = WasteProfileForm(request.POST, instance=waste_info)
#         if form.is_valid():
#             waste_info = form.save()

#             selected_date_id = request.POST.get("selected_date")
#             if selected_date_id:
#                 try:
#                     cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                     CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={"localbody_calendar": cal}
#                     )
#                 except LocalBodyCalendar.DoesNotExist:
#                     messages.warning(request, "⚠️ Invalid pickup date selected.")

#             messages.success(request, "✅ Waste profile updated successfully.")
#             return redirect("super_admin_dashboard:waste_info_list")
#     else:
#         form = WasteProfileForm(instance=waste_info)

#     available_dates = LocalBodyCalendar.objects.filter(localbody=waste_info.localbody).order_by("date")
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {districts.count()}")
#     print(f"DEBUG: LocalBodies count: {localbodies.count()}")
#     print(f"DEBUG: Selected filters - District: {request.GET.get('district_filter')}, LocalBody: {request.GET.get('localbody_filter')}, Phone: {request.GET.get('phone_filter')}")

#     return render(request, "superadmin_edit_waste.html", {
#         "form": form,
#         "info": waste_info,
#         "existing_pickups": existing_pickups,
#         "available_dates": available_dates,
#         "districts": districts,
#         "localbodies": localbodies
#     })



# @login_required
# def delete_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     if request.method == "POST":
#         waste_info.delete()
#         messages.success(request, "🗑️ Waste profile deleted successfully.")
#         return redirect("super_admin_dashboard:waste_info_list")  # ✅ updated

#     return render(request, "superadmin_confirm_delete.html", {
#         "info": waste_info
#     })


# from django.core.paginator import Paginator
# from django.db.models import Q

# @login_required
# def waste_info_list(request):
#     search_query = request.GET.get("q", "")   # search input
#     page_number = request.GET.get("page", 1)  # current page

#     # Fetch all customer waste profiles
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         "state", "district", "localbody", "assigned_collector", "user"
#     ).prefetch_related("customerpickupdate_set__localbody_calendar")

#     # ✅ Search filter (name / phone / address)
#     if search_query:
#         waste_infos = waste_infos.filter(
#             Q(user__first_name__icontains=search_query) |
#             Q(user__last_name__icontains=search_query) |
#             Q(user__contact_number__icontains=search_query) |
#             Q(pickup_address__icontains=search_query)
#         )

#     # ✅ Pagination (10 profiles per page)
#     paginator = Paginator(waste_infos.order_by("-id"), 10)
#     page_obj = paginator.get_page(page_number)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     return render(request, "waste_info_list.html", {
#         "page_obj": page_obj,
#         "collectors": collectors,
#         "search_query": search_query,
#     })

# @login_required
# @user_passes_test(is_super_admin)
# def load_localbodies_for_reports(request):
#     district_id = request.GET.get('district_id')
#     localbodies = LocalBody.objects.filter(district_id=district_id).values("id", "name") if district_id else []
#     return JsonResponse(list(localbodies), safe=False)

# @login_required
# @user_passes_test(is_super_admin)
# def generate_reports(request):
#     """
#     View to display the reports page.
#     """
#     return render(request, 'reports.html')

# @login_required
# @user_passes_test(is_super_admin)
# def generate_report(request):
#     """Generate various types of reports"""
#     if request.method == 'POST':
#         try:
#             report_type = request.POST.get('report_type')
#             print(f"Generating report type: {report_type}")

#             # Get real data for reports
#             from customer_dashboard.models import CustomerWasteInfo
#             from authentication.models import CustomUser
#             from waste_collector_dashboard.models import WasteCollection
#             from datetime import date, datetime, timedelta

#             # Initialize report data
#             report_data = {
#                 'report_type': report_type,
#                 'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                 'report_name': f"{report_type.replace('_', ' ').title()} Report"
#             }

#             # Generate specific report data based on type
#             if report_type == 'daily_collection':
#                 # Get today's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date=today
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'collections_data': [{
#                         'customer': col.customer.get_full_name() if col.customer else 'Unknown',
#                         'address': col.location,
#                         'waste_type': col.customer.customerwasteinfo_set.first().waste_type if col.customer and col.customer.customerwasteinfo_set.exists() else 'Unknown',
#                         'bags': col.number_of_bags,
#                         'collected_at': col.collection_time.strftime('%H:%M') if col.collection_time else 'N/A'
#                     } for col in collections]
#                 })

#             elif report_type == 'weekly_collection':
#                 # Get this week's collections
#                 today = date.today()
#                 week_start = today - timedelta(days=today.weekday())
#                 week_end = week_start + timedelta(days=6)

#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__range=[week_start, week_end]
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
#                 })

#             elif report_type == 'monthly_collection':
#                 # Get this month's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__year=today.year,
#                     scheduled_date__month=today.month
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': today.strftime('%B %Y')
#                 })

#             elif report_type == 'customer_summary':
#                 # Get customer summary data
#                 customers = CustomUser.objects.filter(role=0)
#                 total_customers = customers.count()
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).count()

#                 report_data.update({
#                     'total_customers': total_customers,
#                     'active_customers': active_customers,
#                     'new_customers_this_month': active_customers
#                 })

#             elif report_type == 'active_customers':
#                 # Get active customers
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).select_related('user', 'state', 'district', 'localbody')

#                 report_data.update({
#                     'total_active_customers': active_customers.count(),
#                     'customer_list': [{
#                         'name': info.user.get_full_name() if info.user else 'Unknown',
#                         'phone': info.user.contact_number if hasattr(info.user, 'contact_number') else 'N/A',
#                         'address': info.pickup_address if hasattr(info, 'pickup_address') else 'N/A',
#                         'waste_type': info.waste_type,
#                         'status': info.status,
#                         'last_collection': 'N/A',
#                         'days_since_last': 'N/A'
#                     } for info in active_customers]
#                 })

#             elif report_type == 'payment_analysis':
#                 report_data.update({
#                     'payment_analysis': 'Payment analysis data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'outstanding_payments':
#                 report_data.update({
#                     'outstanding_payments': 'Outstanding payments data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'collector_performance':
#                 # Analyze collector performance
#                 collectors = CustomUser.objects.filter(role=1)
#                 performance_data = []

#                 for collector in collectors:
#                     try:
#                         # Get collections for this collector this month
#                         collector_collections = WasteCollection.objects.filter(
#                             collector=collector,
#                             scheduled_date__month=date.today().month,
#                             scheduled_date__year=date.today().year
#                         )

#                         total_collections = collector_collections.count()
#                         total_bags = sum(col.number_of_bags for col in collector_collections)

#                         performance_data.append({
#                             'collector_name': collector.get_full_name(),
#                             'total_collections': total_collections,
#                             'total_bags': total_bags,
#                             'days_worked': len(set(col.scheduled_date for col in collector_collections if col.scheduled_date)),
#                         })
#                     except Exception as e:
#                         print(f"Error processing collector {collector.id}: {e}")
#                         continue

#                 # Sort by performance
#                 performance_data.sort(key=lambda x: x['total_collections'], reverse=True)

#                 report_data.update({
#                     'period': date.today().strftime('%B %Y'),
#                     'total_collectors': len(collectors),
#                     'performance_data': performance_data,
#                     'top_performers': performance_data[:5]
#                 })

#             elif report_type == 'efficiency_metrics':
#                 report_data.update({
#                     'efficiency_metrics': 'Operational efficiency metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'service_level':
#                 report_data.update({
#                     'service_level': 'Service level metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             else:
#                 return JsonResponse({'success': False, 'error': f'Unknown report type: {report_type}'}, status=400)

#             print("Report generated successfully:", report_data)
#             return JsonResponse({
#                 'success': True,
#                 'report_data': report_data,
#                 'report_name': report_data['report_name']
#             })

#         except Exception as e:
#             error_msg = str(e)
#             print("Error generating report:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# @login_required
# @user_passes_test(is_super_admin)
# def load_districts_for_reports(request):
#     state_id = request.GET.get('state_id')
#     districts = District.objects.filter(state_id=state_id).values("id", "name") if state_id else []
#     return JsonResponse(list(districts), safe=False)


#   # Get additional data for CRUD functionality
#     from authentication.models import CustomUser
#     from super_admin_dashboard.models import LocalBody

#     all_customers = CustomUser.objects.filter(role=0)  # Customers
#     all_localbodies = LocalBody.objects.all()

#     try:
#         response = render(request, 'view_collected_data.html', {
#             'all_data': all_data,
#             'all_customers': all_customers,
#             'all_localbodies': all_localbodies,
#         })
#         print("Template rendered successfully")
#         print("=======================================")
#         return response
#     except Exception as e:
#         print(f"ERROR rendering template: {e}")
#         import traceback
#         traceback.print_exc()
#         raise


# # CRUD Operations for Waste Collection
# @login_required
# @user_passes_test(can_view_collected_data)
# def update_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)

#         # Update fields based on POST data
#         waste_collection.ward = request.POST.get('ward', waste_collection.ward)
#         waste_collection.location = request.POST.get('location', waste_collection.location)
#         waste_collection.number_of_bags = request.POST.get('number_of_bags', waste_collection.number_of_bags)
#         waste_collection.building_no = request.POST.get('building_no', waste_collection.building_no)
#         waste_collection.street_name = request.POST.get('street_name', waste_collection.street_name)
#         waste_collection.kg = request.POST.get('kg', waste_collection.kg)

#         # Handle customer and localbody foreign keys
#         if request.POST.get('customer'):
#             customer_id = int(request.POST.get('customer'))
#             waste_collection.customer = CustomUser.objects.get(id=customer_id, role=0)

#         if request.POST.get('localbody'):
#             localbody_id = int(request.POST.get('localbody'))
#             waste_collection.localbody = LocalBody.objects.get(id=localbody_id)

#         # Handle date fields
#         scheduled_date_str = request.POST.get('scheduled_date')
#         if scheduled_date_str:
#             waste_collection.scheduled_date = scheduled_date_str
#         elif scheduled_date_str == '':
#             waste_collection.scheduled_date = None

#         # Handle time field
#         collection_time_str = request.POST.get('collection_time')
#         if collection_time_str:
#             from datetime import datetime
#             time_obj = datetime.strptime(collection_time_str, '%H:%M').time()
#             waste_collection.collection_time = time_obj
#         elif collection_time_str == '':
#             waste_collection.collection_time = None

#         # Recalculate total amount if kg or rate changes
#         waste_collection.save()

#         return JsonResponse({'success': True, 'message': 'Record updated successfully'})

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected customer does not exist'})
#     except LocalBody.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected local body does not exist'})
#     except ValueError as e:
#         return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})


# @login_required
# @user_passes_test(can_view_collected_data)
# def delete_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)
#         waste_collection.delete()
#         return JsonResponse({'success': True, 'message': 'Record deleted successfully'})

#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})







# @login_required
# @user_passes_test(is_super_admin)
# def export_all_users_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"all_users_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Role', 'Contact Number', 'Date Joined'])

#     users = CustomUser.objects.all().order_by('id')

#     for user in users:
#         writer.writerow([
#             user.id,
#             user.username,
#             user.first_name,
#             user.last_name,
#             user.email,
#             user.get_role_display(),
#             user.contact_number,
#             user.date_joined.strftime("%Y-%m-%d %H:%M") if user.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_customers_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"customers_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     customers = CustomUser.objects.filter(role=0)

#     for customer in customers:
#         writer.writerow([
#             customer.id,
#             customer.username,
#             customer.first_name,
#             customer.last_name,
#             customer.email,
#             customer.contact_number,
#             customer.date_joined.strftime("%Y-%m-%d %H:%M") if customer.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_collectors_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"collectors_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     collectors = CustomUser.objects.filter(role=1)

#     for collector in collectors:
#         writer.writerow([
#             collector.id,
#             collector.username,
#             collector.first_name,
#             collector.last_name,
#             collector.email,
#             collector.contact_number,
#             collector.date_joined.strftime("%Y-%m-%d %H:%M") if collector.date_joined else 'N/A'
#         ])

#     return response


# # Test endpoint for debugging with authentication
# @login_required
# @user_passes_test(is_super_admin)
# def test_wards_endpoint(request, localbody_id):
#     """Test endpoint to verify ward loading is working"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse({
#             "status": "success",
#             "localbody_id": localbody_id,
#             "localbody_name": localbody.name,
#             "ward_count": len(data),
#             "wards": data
#         })
#     except LocalBody.DoesNotExist:
#         return JsonResponse({
#             "status": "error",
#             "message": "Local body not found"
#         }, status=404)
#     except Exception as e:
#         return JsonResponse({
#             "status": "error",
#             "message": str(e)
#         }, status=500)


# # Price Control Views
# @login_required
# @user_passes_test(is_super_admin)
# def price_control(request):
#     """Price control page for managing waste collection pricing"""
#     from django.urls import reverse
#     from .models import District, LocalBody, WasteTypePrice, ServiceFee, LocationPriceMultiplier, PriceControl

#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Get existing pricing data
#     waste_prices = WasteTypePrice.objects.all()
#     service_fee = ServiceFee.objects.first()
#     location_multipliers = LocationPriceMultiplier.objects.select_related('district', 'localbody').all()
#     area_prices = PriceControl.objects.select_related('district', 'localbody').all()

#     # Base URLs for cascading dropdowns
#     try:
#         url_localbodies_base = reverse('adminpanel:load_localbodies', args=[0]).replace('/0/', '/')
#     except Exception:
#         url_localbodies_base = '/admin/calendar/localbodies/'
#     try:
#         url_wards_base = reverse('adminpanel:load_wards', args=[0]).replace('/0/', '/')
#     except Exception:
#         url_wards_base = '/admin/calendar/wards/'

#     context = {
#         'districts': districts,
#         'localbodies': localbodies,
#         'waste_prices': waste_prices,
#         'service_fee': service_fee,
#         'location_multipliers': location_multipliers,
#         'area_prices': area_prices,
#         'url_localbodies_base': url_localbodies_base,
#         'url_wards_base': url_wards_base,
#     }
#     return render(request, 'price_control.html', context)


# @login_required
# @user_passes_test(is_super_admin)
# def load_price_history(request):
#     """Load price history for display"""
#     if request.method == 'GET':
#         try:
#             from .models import PriceHistory
#             from django.core.serializers.json import DjangoJSONEncoder

#             history = PriceHistory.objects.select_related('updated_by').order_by('-created_at')[:20]

#             history_data = []
#             for item in history:
#                 history_data.append({
#                     'date': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                     'type': item.pricing_type.replace('_', ' ').title(),
#                     'category': item.category,
#                     'old_price': f"₹{item.old_value}" if item.old_value else '-',
#                     'new_price': f"₹{item.new_value}" if item.new_value else '-',
#                     'updated_by': item.updated_by.get_full_name() if item.updated_by else 'System',
#                     'status': 'active' if item.action_type == 'create' else 'updated'
#                 })

#             return JsonResponse({
#                 'success': True,
#                 'data': history_data
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_waste_price(request):
#     """Save waste type pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import WasteTypePrice, PriceHistory
#             data = json.loads(request.body)

#             waste_type = data.get('waste_type')
#             price_per_kg = data.get('price_per_kg')
#             status = data.get('status', 'active')

#             # Validate input
#             if not waste_type or price_per_kg is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             price_per_kg = float(price_per_kg)
#             if price_per_kg < 0:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price must be non-negative'
#                 })

#             # Get or create waste type price
#             waste_price, created = WasteTypePrice.objects.get_or_create(
#                 waste_type=waste_type,
#                 defaults={
#                     'price_per_kg': price_per_kg,
#                     'status': status,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_price = waste_price.price_per_kg
#                 waste_price.price_per_kg = price_per_kg
#                 waste_price.status = status
#                 waste_price.updated_by = request.user
#                 waste_price.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     old_value=old_price,
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Waste type price saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_service_fees(request):
#     """Save service fee pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import ServiceFee, PriceHistory
#             data = json.loads(request.body)

#             base_fee = data.get('base_fee')
#             fee_per_bag = data.get('fee_per_bag')
#             min_charge = data.get('min_charge')

#             # Validate input
#             if base_fee is None or fee_per_bag is None or min_charge is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             base_fee = float(base_fee)
#             fee_per_bag = float(fee_per_bag)
#             min_charge = float(min_charge)

#             if any(x < 0 for x in [base_fee, fee_per_bag, min_charge]):
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'All fees must be non-negative'
#                 })

#             # Get or create service fee
#             service_fee, created = ServiceFee.objects.get_or_create(
#                 pk=1,  # Assume single service fee record
#                 defaults={
#                     'base_fee': base_fee,
#                     'fee_per_bag': fee_per_bag,
#                     'min_charge': min_charge,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_base_fee = service_fee.base_fee
#                 old_fee_per_bag = service_fee.fee_per_bag
#                 old_min_charge = service_fee.min_charge

#                 service_fee.base_fee = base_fee
#                 service_fee.fee_per_bag = fee_per_bag
#                 service_fee.min_charge = min_charge
#                 service_fee.updated_by = request.user
#                 service_fee.save()

#                 # Log changes to history
#                 if old_base_fee != base_fee:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Base Fee',
#                         old_value=old_base_fee,
#                         new_value=base_fee,
#                         updated_by=request.user
#                     )

#                 if old_fee_per_bag != fee_per_bag:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Fee per Bag',
#                         old_value=old_fee_per_bag,
#                         new_value=fee_per_bag,
#                         updated_by=request.user
#                     )

#                 if old_min_charge != min_charge:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Minimum Charge',
#                         old_value=old_min_charge,
#                         new_value=min_charge,
#                         updated_by=request.user
#                     )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='service_fee',
#                     category='Service Fees',
#                     new_value=base_fee,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Service fees saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_location_multiplier(request):
#     """Save location-based price multiplier"""
#     if request.method == 'POST':
#         try:
#             from .models import LocationPriceMultiplier, PriceHistory, District, LocalBody
#             data = json.loads(request.body)

#             # Validate price multiplier
#             price_multiplier = float(data.get('price_multiplier', 0))
#             if price_multiplier > 500.0 or price_multiplier < 0.1:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price multiplier must be between 0.1 and 500.0'
#                 })

#             district_id = data.get('district')
#             localbody_id = data.get('localbody')

#             if not district_id or not localbody_id:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'District and Local Body are required'
#                 })

#             # Get district and localbody objects
#             district = District.objects.get(id=district_id)
#             localbody = LocalBody.objects.get(id=localbody_id)

#             # Get or create location price multiplier
#             location_multiplier, created = LocationPriceMultiplier.objects.get_or_create(
#                 district=district,
#                 localbody=localbody,
#                 defaults={
#                     'price_multiplier': price_multiplier,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_multiplier = location_multiplier.price_multiplier
#                 location_multiplier.price_multiplier = price_multiplier
#                 location_multiplier.updated_by = request.user
#                 location_multiplier.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     old_value=old_multiplier,
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Location multiplier saved successfully'
#             })
#         except ValueError:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid price multiplier value'
#             })
#         except District.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'District not found'
#             })
#         except LocalBody.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Local Body not found'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_area_price(request):
#     """Save area price (District + Local Body + Ward → price per KG)."""
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})
#     try:
#         from decimal import Decimal
#         from .models import PriceControl, PriceHistory, District, LocalBody

#         data = json.loads(request.body)
#         district_id = data.get('district_id')
#         localbody_id = data.get('localbody_id')
#         ward = (data.get('ward') or '').strip()
#         price_per_kg = data.get('price_per_kg')

#         if not district_id or not localbody_id or not ward or price_per_kg is None:
#             return JsonResponse({'success': False, 'error': 'District, Local Body, Ward and Price are required'})

#         district = get_object_or_404(District, id=district_id)
#         localbody = get_object_or_404(LocalBody, id=localbody_id)
#         if localbody.district_id != district.id:
#             return JsonResponse({'success': False, 'error': 'Local body does not belong to selected district'})

#         price_decimal = Decimal(str(price_per_kg))
#         if price_decimal < 0:
#             return JsonResponse({'success': False, 'error': 'Price must be non-negative'})

#         obj, created = PriceControl.objects.get_or_create(
#             district=district,
#             localbody=localbody,
#             ward=ward,
#             defaults={'price_per_kg': price_decimal, 'updated_by': request.user}
#         )

#         category = f"{district.name} / {localbody.name} / {ward}"
#         if created:
#             PriceHistory.objects.create(
#                 action_type='create',
#                 pricing_type='area_price',
#                 category=category,
#                 new_value=price_decimal,
#                 updated_by=request.user
#             )
#         else:
#             old_price = obj.price_per_kg
#             obj.price_per_kg = price_decimal
#             obj.updated_by = request.user
#             obj.save(update_fields=['price_per_kg', 'updated_by', 'updated_at'])
#             PriceHistory.objects.create(
#                 action_type='update',
#                 pricing_type='area_price',
#                 category=category,
#                 old_value=old_price,
#                 new_value=price_decimal,
#                 updated_by=request.user
#             )

#         return JsonResponse({'success': True, 'message': 'Area price saved successfully'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})


























# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render, redirect,get_object_or_404
# from django.http import JsonResponse
# from authentication.models import CustomUser
# from waste_collector_dashboard.models import WasteCollection
# # from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate  # Moved inside functions to avoid circular import
# from django.contrib import messages
# from .utils import is_super_admin
# from django.template.loader import get_template, render_to_string
# from django.utils import timezone
# from django.db.models import Sum
# from datetime import datetime
# from .models import State, District, LocalBody, LocalBodyCalendar, Ward

# def get_ward_names():
#     """Return a dictionary mapping ward numbers to ward names"""
#     return {
#         1: "Fort Kochi",
#         2: "Kalvathy",
#         3: "Earavely",
#         4: "Karippalam",
#         5: "Cheralayi",
#         6: "Mattanchery",
#         7: "Chakkamadam",
#         8: "Karuvelippady",
#         9: "Island North",
#         10: "Ravipuram",
#         11: "Ernakulam South",
#         12: "Gandhi Nagar",
#         13: "Kathrikadavu",
#         14: "Ernakulam Central",
#         15: "Ernakulam North",
#         16: "Kaloor South",
#         17: "Kaloor North",
#         18: "Thrikkanarvattom",
#         19: "Ayyappankavu",
#         20: "Pottakuzhy",
#         21: "Elamakkara South",
#         22: "Pachalam",
#         23: "Thattazham",
#         24: "Vaduthala West",
#         25: "Vaduthala East",
#         26: "Elamakkara North",
#         27: "Puthukkalavattam",
#         28: "Kunnumpuram",
#         29: "Ponekkara",
#         30: "Edappally",
#         31: "Changampuzha",
#         32: "Dhevankulangara",
#         33: "Palarivattom",
#         34: "Stadium",
#         35: "Karanakkodam",
#         36: "Puthiyaroad",
#         37: "Padivattam",
#         38: "Vennala",
#         39: "Chakkaraparambu",
#         40: "Chalikkavattam",
#         41: "Thammanam",
#         42: "Elamkulam",
#         43: "Girinagar",
#         44: "Ponnurunni",
#         45: "Ponnurunni East",
#         46: "Vyttila",
#         47: "Poonithura",
#         48: "Vyttila Janatha",
#         49: "Kadavanthra",
#         50: "Panampilly Nagar",
#         51: "Perumanoor",
#         52: "Konthuruthy",
#         53: "Thevara",
#         54: "Island South",
#         55: "Kadebhagam",
#         56: "Palluruthy East",
#         57: "Thazhuppu",
#         58: "Eadakochi North",
#         59: "Edakochi South",
#         60: "Perumbadappu",
#         61: "Konam",
#         62: "Palluruthy Kacheripady",
#         63: "Nambyapuram",
#         64: "Palluruthy",
#         65: "Pullardesam",
#         66: "Tharebhagam",
#         67: "Thoppumpady",
#         68: "Mundamvely East",
#         69: "Mundamvely",
#         70: "Manassery",
#         71: "Moolamkuzhy",
#         72: "Chullickal",
#         73: "Nasrathu",
#         74: "Panayappilly",
#         75: "Amaravathy",
#         76: "Fortkochi Veli"
#     }

# def get_ward_options(localbody_name=None):
#     """Kochi/Ernakulam → 76 named wards (Fort Kochi, etc.); other local bodies → Ward 1 to Ward 10."""
#     ward_names = get_ward_names()
#     name_lower = (localbody_name or '').lower()
#     if name_lower and ('kochi' in name_lower or 'ernakulam' in name_lower):
#         return [(i, ward_names.get(i, f'Ward {i}')) for i in range(1, 77)]
#     return [(i, f'Ward {i}') for i in range(1, 11)]


# @login_required
# def admin_home(request):
#     from customer_dashboard.models import CustomerPickupDate, CustomerWasteInfo
#     from django.db.models import Count, Q

#     # Get current date info
#     now = timezone.now()
#     first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

#     # Calculate statistics
#     total_customers = CustomUser.objects.filter(role=0).count()
#     total_collectors = CustomUser.objects.filter(role=1).count()

#     # Collections this month
#     monthly_collections = WasteCollection.objects.filter(
#         created_at__gte=first_day_of_month
#     ).count()

#     # Total waste collected (sum of kg)
#     total_waste_collected_data = WasteCollection.objects.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     # 1. Collection Rate: Collections vs Scheduled Pickups
#     scheduled_pickups = CustomerPickupDate.objects.filter(
#         localbody_calendar__date__gte=first_day_of_month.date(),
#         localbody_calendar__date__lte=now.date()
#     ).count()

#     collection_rate = 0
#     if scheduled_pickups > 0:
#         collection_rate = min(100, int((monthly_collections / scheduled_pickups) * 100))
#     elif monthly_collections > 0:
#         collection_rate = 100

#     # 2. Customer Satisfaction: Based on "On-Time" collections
#     # If scheduled_date == collection_date or matches within 1 day
#     on_time_collections = 0
#     total_with_schedule = 0
#     collections_with_schedule = WasteCollection.objects.filter(
#         scheduled_date__isnull=False,
#         created_at__gte=first_day_of_month
#     )

#     for coll in collections_with_schedule:
#         total_with_schedule += 1
#         # Compare created_at date with scheduled_date
#         collection_date = coll.created_at.date()
#         scheduled_date = coll.scheduled_date

#         # Ensure we are comparing date to date (scheduled_date might be datetime in some cases)
#         if hasattr(scheduled_date, 'date'):
#             scheduled_date = scheduled_date.date()

#         if collection_date <= scheduled_date:
#             on_time_collections += 1

#     customer_satisfaction = 4.5 # Default high starting point
#     if total_with_schedule > 0:
#         satisfaction_ratio = on_time_collections / total_with_schedule
#         customer_satisfaction = round(3.0 + (satisfaction_ratio * 2.0), 1) # Scale between 3.0 and 5.0

#     # 3. Recycling Rate: Estimated based on waste types
#     # Check CustomerWasteInfo for recyclable types
#     recyclable_keywords = ['plastic', 'paper', 'metal', 'glass', 'can', 'bottle', 'recyclable']
#     recyclable_query = Q()
#     for kw in recyclable_keywords:
#         recyclable_query |= Q(waste_type__icontains=kw)

#     total_profiles = CustomerWasteInfo.objects.count()
#     recyclable_profiles = CustomerWasteInfo.objects.filter(recyclable_query).count()

#     recycling_rate = 0
#     if total_profiles > 0:
#         recycling_rate = int((recyclable_profiles / total_profiles) * 100)
#     else:
#         recycling_rate = 65 # Reasonable industry average placeholder if no data

#     # Get order data for control all orders functionality
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'user', 'state', 'district', 'localbody', 'assigned_collector'
#     ).all()

#     total_orders = waste_infos.count()
#     pending_orders = waste_infos.filter(status='pending').count()
#     confirmed_orders = waste_infos.filter(status='in_progress').count()
#     completed_orders = waste_infos.filter(status='completed').count()

#     # Get all collectors for dropdown
#     collectors = CustomUser.objects.filter(role=1)

#     # Build orders data from real CustomerWasteInfo
#     orders = []
#     for info in waste_infos[:20]:  # Limit to first 20 orders
#         try:
#             # Get scheduled date for this waste info
#             pickup_date = info.customerpickupdate_set.select_related('localbody_calendar').first()
#             scheduled_date_order = pickup_date.localbody_calendar.date.strftime('%Y-%m-%d') if pickup_date and pickup_date.localbody_calendar else 'Not Scheduled'

#             # Get assigned collector name
#             collector_name = info.assigned_collector.get_full_name() if info.assigned_collector else 'Unassigned'

#             # Convert status to readable format
#             status_map = {
#                 'pending': 'Pending',
#                 'in_progress': 'In Progress',
#                 'completed': 'Completed',
#                 'collected': 'Collected'
#             }
#             readable_status = status_map.get(info.status, info.status)

#             order = {
#                 'id': info.id,
#                 'customer_name': info.full_name,
#                 'customer_phone': info.user.contact_number,
#                 'address': info.pickup_address,
#                 'waste_type': info.waste_type,
#                 'bags': info.number_of_bags or 0,
#                 'booking_date': info.created_at.strftime('%Y-%m-%d'),
#                 'scheduled_date': scheduled_date_order,
#                 'status': readable_status,
#                 'assigned_collector': collector_name,
#                 'ward': info.ward,
#                 'localbody': info.localbody.name if info.localbody else 'Not Assigned'
#             }
#             orders.append(order)
#         except Exception as e:
#             print(f"Error processing order {info.id}: {e}")
#             continue

#     context = {
#         'total_customers': total_customers,
#         'total_collectors': total_collectors,
#         'monthly_collections': monthly_collections,
#         'total_waste_collected': f"{total_waste_collected_data:.1f} KG",
#         'collection_rate': collection_rate,
#         'customer_satisfaction': customer_satisfaction,
#         'recycling_rate': recycling_rate,
#         'orders': orders,
#         'total_orders': total_orders,
#         'pending_orders': pending_orders,
#         'confirmed_orders': confirmed_orders,
#         'completed_orders': completed_orders,
#         'collectors': collectors
#     }

#     return render(request, 'super_admin_dashboard.html', context)


# @login_required
# def manage_order(request, order_id):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     # Add logging for debugging
#     print(f"manage_order called with order_id: {order_id}, method: {request.method}")
#     print(f"User authenticated: {request.user.is_authenticated}")
#     print(f"User: {request.user}")

#     if request.method == 'POST':
#         try:
#             action = request.POST.get('action')
#             print(f"Action: {action}")

#             # Get the waste info object
#             waste_info = CustomerWasteInfo.objects.get(id=order_id)
#             print(f"Waste info found: {waste_info.id}")

#             # Handle order management actions
#             if action == 'assign_collector':
#                 collector_id = request.POST.get('collector_id')
#                 print(f"Assigning collector: {collector_id}")
#                 if collector_id:
#                     collector = CustomUser.objects.get(id=collector_id, role=1)  # role=1 for collectors
#                     waste_info.assigned_collector = collector
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} assigned to collector successfully')
#                     print("Collector assigned successfully")

#             elif action == 'update_status':
#                 new_status = request.POST.get('status')
#                 print(f"Updating status to: {new_status}")
#                 if new_status in ['pending', 'in_progress', 'completed', 'collected']:
#                     waste_info.status = new_status
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} status updated to {new_status}')
#                     print("Status updated successfully")

#             elif action == 'reschedule':
#                 new_date = request.POST.get('new_date')
#                 print(f"Rescheduling to: {new_date}")
#                 if new_date:
#                     # First get or create the calendar entry if it doesn't exist
#                     calendar_entry, created = LocalBodyCalendar.objects.get_or_create(
#                         localbody=waste_info.localbody,
#                         date=new_date
#                     )
#                     # Update the scheduled date by creating/updating the CustomerPickupDate
#                     pickup_date, created = CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={'localbody_calendar': calendar_entry}
#                     )
#                     messages.success(request, f'Order {order_id} rescheduled to {new_date}')
#                     print("Order rescheduled successfully")

#             response_data = {'success': True}
#             print("Returning success response:", response_data)
#             return JsonResponse(response_data)

#         except CustomerWasteInfo.DoesNotExist:
#             error_msg = f'Order {order_id} not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except CustomUser.DoesNotExist:
#             error_msg = 'Collector not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except LocalBodyCalendar.DoesNotExist:
#             error_msg = 'Schedule date not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except Exception as e:
#             error_msg = str(e)
#             print("Unexpected error:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     # If not POST method
#     error_msg = 'Invalid request method'
#     print("Error:", error_msg)
#     return JsonResponse({'success': False, 'error': error_msg}, status=405)


# @login_required
# def user_list_view(request):
#     customers = CustomUser.objects.filter(role=0)
#     collectors = CustomUser.objects.filter(role=1)
#     admins = CustomUser.objects.filter(role=2)

#     return render(request, 'user_list.html', {
#         'customers': customers,
#         'collectors': collectors,
#         'admins': admins,
#     })
# @login_required
# def view_customers(request):
#     customers = CustomUser.objects.filter(role=0)
#     return render(request, 'view_customers.html', {'customers': customers})

# @login_required
# def view_waste_collectors(request):
#     collectors = CustomUser.objects.filter(role=1)
#     total_collectors = collectors.count()
#     service_areas = CollectorServiceArea.objects.select_related(
#         'collector', 'district', 'localbody'
#     ).order_by('collector__username', 'district__name', 'localbody__name')

#     # Get data for dropdowns (same style as view_collected_data)
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')  # kept for fallback/template safety

#     # Local body dropdown URL (login-only endpoint; filtered by district)
#     try:
#         load_localbodies_url = request.build_absolute_uri(
#             reverse('adminpanel:load_localbodies_collectors', args=[0])
#         ).replace('/0/', '/')
#     except Exception:
#         load_localbodies_url = request.build_absolute_uri('/admin/users/collectors/load-localbodies/')

#     # Ward dropdown URL (login-only endpoint for collectors page)
#     from django.urls import reverse
#     try:
#         load_wards_url = request.build_absolute_uri(
#             reverse('adminpanel:load_wards_collectors', args=[0])
#         ).replace('/0/', '/')
#     except Exception:
#         load_wards_url = request.build_absolute_uri('/admin/users/collectors/load-wards/')

#     return render(request, 'view_collectors.html', {
#         'collectors': collectors,
#         'total_collectors': total_collectors,
#         'service_areas': service_areas,
#         'districts': districts,
#         'localbodies': localbodies,
#         'load_localbodies_url': load_localbodies_url,
#         'load_wards_url': load_wards_url,
#     })
# @login_required
# def view_super_admin(request):
#     super_admin = CustomUser.objects.filter(role=2)
#     return render(request, "view_super_admin.html", {"super_admin":super_admin})

# @login_required
# def view_admins(request):
#     admins = CustomUser.objects.filter(role=3)
#     return render(request, "view_admins.html", {"admins":admins})

# # \\\\\\\\\\\\\\\\\\\\\\\\\\\ user view //////////////////////

# from .forms import UserForm

# @login_required
# def user_list(request):
#     users = CustomUser.objects.all()
#     return render(request, "users_list.html", {"users": users})





# @login_required
# def user_create(request):
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Encrypt password before saving
#                 user.set_password(password)
#             else:  # Default password if none provided
#                 user.set_password("default123")
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm()
#     return render(request, 'user_form.html', {'form': form})

# # Update User
# @login_required
# def user_update(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == 'POST':
#         form = UserForm(request.POST, instance=user)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Reset password if admin entered new one
#                 user.set_password(password)
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm(instance=user)
#     return render(request, 'user_form.html', {'form': form, 'user': user})






# # Delete user
# @login_required
# def user_delete(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         user.delete()
#         messages.success(request, "User deleted successfully")
#         return redirect("super_admin_dashboard:users_list")
#     return render(request, "user_confirm_delete.html", {"user": user})



# from django.shortcuts import render
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser

# @login_required
# def view_customer_wasteinfo(request):
#     # Fetch only unassigned customer waste profiles with related fields
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'state', 'district', 'localbody', 'assigned_collector', 'user'
#     ).filter(assigned_collector__isnull=True)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     # Map waste_info_id → pickup date
#     pickup_dates = {}
#     pickups = CustomerPickupDate.objects.select_related('localbody_calendar', 'waste_info').all()
#     for pickup in pickups:
#         if pickup.waste_info:
#             pickup_dates[pickup.waste_info.id] = pickup.localbody_calendar.date

#     return render(request, 'view_customer_wasteinfo.html', {
#         'waste_infos': waste_infos,
#         'collectors': collectors,
#         'pickup_dates': pickup_dates,
#     })

# # Assign a waste collector to a CustomerWasteInfo entry
# @login_required
# def assign_waste_collector(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)
#     if request.method == 'POST':
#         collector_id = request.POST.get('collector')
#         collector = get_object_or_404(CustomUser, pk=collector_id, role=1)

#         # Store customer info for success message
#         customer_name = waste_info.user.username
#         customer_address = waste_info.pickup_address

#         # Assign collector and ensure is_collected is False so it appears in assigned customers list
#         waste_info.assigned_collector = collector
#         waste_info.is_collected = False  # Mark as not collected so collector can see it
#         waste_info.save()

#         messages.success(request, f"Customer {customer_name} at {customer_address} has been assigned to {collector.username}. The customer now appears in the collector's assigned customers list.")
#         return redirect('super_admin_dashboard:view_customer_waste_info')

#     collectors = CustomUser.objects.filter(role=1)
#     return render(request, 'assign_waste_collector.html', {
#         'waste_info': waste_info,
#         'collectors': collectors,
#     })


# #waste collector collect details from customer

# def can_view_collected_data(user):
#     # Role 1 is Collector, Role 2 is Super Admin
#     return user.is_authenticated and (getattr(user, 'role', None) in [1, 2] or user.is_superuser)

# @login_required
# @user_passes_test(can_view_collected_data)
# def view_collected_data(request):
#     # Get waste collection data with related information
#     user_role = getattr(request.user, 'role', None)
#     try:
#         user_role = int(user_role)
#     except (TypeError, ValueError):
#         user_role = None

#     # Get filter parameters
#     district_filter = request.GET.get('district')
#     localbody_filter = request.GET.get('localbody')
#     phone_filter = request.GET.get('phone')
#     from_date_filter = request.GET.get('from_date')
#     to_date_filter = request.GET.get('to_date')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {District.objects.count()}")
#     print(f"DEBUG: LocalBodies count: {LocalBody.objects.count()}")
#     print(f"DEBUG: Selected filters - District: {district_filter}, LocalBody: {localbody_filter}, Phone: {phone_filter}")

#     # Base queryset
#     if user_role == 1:
#         # Collector (Role 1) sees only their own data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).filter(collector=request.user)
#     else:
#         # Admin (Role 2) or others see all data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).all()

#     # Apply filters
#     if district_filter:
#         all_data = all_data.filter(localbody__district__id=district_filter)

#     if localbody_filter:
#         all_data = all_data.filter(localbody__id=localbody_filter)

#     if phone_filter:
#         all_data = all_data.filter(
#             Q(customer__contact_number__icontains=phone_filter) |
#             Q(collector__contact_number__icontains=phone_filter)
#         )

#     if from_date_filter:
#         try:
#             from_date = datetime.strptime(from_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__gte=from_date)
#         except ValueError:
#             pass

#     if to_date_filter:
#         try:
#             to_date = datetime.strptime(to_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__lte=to_date)
#         except ValueError:
#             pass

#     # Filter by month if requested (legacy functionality)
#     month_filter = request.GET.get('month')
#     if month_filter == 'current':
#         from django.utils import timezone
#         now = timezone.now()
#         first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         all_data = all_data.filter(created_at__gte=first_day_of_month)

#     # Order by created_at descending
#     all_data = all_data.order_by('-created_at')

#     # Get districts and localbodies for filter dropdowns
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Final districts count: {districts.count()}")
#     print(f"DEBUG: Final localbodies count: {localbodies.count()}")
#     print(f"DEBUG: Filtered data count: {all_data.count()}")

#     # Handle AJAX request for filtered data
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         # Prepare data for JSON response
#         data = []
#         for item in all_data:
#             data.append({
#                 'id': item.id,
#                 'collector': item.collector.username,
#                 'customer': item.customer.username,
#                 'localbody': item.localbody.name if item.localbody else 'Not assigned',
#                 'ward': item.ward,
#                 'location': item.location,
#                 'number_of_bags': item.number_of_bags,
#                 'building_no': item.building_no,
#                 'street_name': item.street_name,
#                 'kg': float(item.kg),
#                 'total_amount': float(item.total_amount) if item.total_amount else 0,
#                 'payment_method': item.get_payment_method_display(),
#                 'photo_url': item.photo.url if item.photo else None,
#                 'booking_date': item.booking_date.strftime('%Y-%m-%d %H:%M') if item.booking_date else '',
#                 'collection_time': item.collection_time.strftime('%H:%M') if item.collection_time else '',
#                 'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                 'scheduled_date': item.scheduled_date.strftime('%Y-%m-%d') if item.scheduled_date else '',
#             })

#         return JsonResponse({
#             'data': data,
#             'total_count': len(data)
#         })

#     return render(request, 'view_collected_data.html', {
#         'all_data': all_data,
#         'districts': districts,
#         'localbodies': localbodies,
#         'selected_district': district_filter,
#         'selected_localbody': localbody_filter,
#         'selected_phone': phone_filter,
#         'selected_from_date': from_date_filter,
#         'selected_to_date': to_date_filter,
#         'all_data': all_data
#     })


# # ////// MAP_ROLE
# @login_required
# def map_role(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         new_role = request.POST.get("role")
#         if new_role is not None:
#             try:
#                 new_role = int(new_role)  # Convert string to int
#                 if new_role in dict(CustomUser.ROLE_CHOICES).keys():
#                     user.role = new_role
#                     user.save()
#                     return redirect("super_admin_dashboard:users_list")
#             except ValueError:
#                 pass  # Ignore invalid input
#     return render(request, "map_role.html", {"user": user, "roles": CustomUser.ROLE_CHOICES})







# # ////////////////////////////      CALENDAR SET UP     ///////////////////////////////////


# import json
# from datetime import date, datetime, timedelta

# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
# from django.views.decorators.http import require_POST, require_GET
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.utils.dateparse import parse_date
# from django.template.loader import get_template


# from .models import State, District, LocalBody, LocalBodyCalendar
# from .utils import is_super_admin





# @login_required
# @user_passes_test(is_super_admin)
# def calendar_view(request):
#     """Main page where admin picks state/district/localbody and sees FullCalendar."""
#     states = State.objects.all().order_by("name")
#     return render(request, "calendar.html", {"states": states})


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_districts(request, state_id):
#     districts = District.objects.filter(state_id=state_id).values("id", "name")
#     return JsonResponse(list(districts), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_localbodies(request, district_id):
#     lbs = LocalBody.objects.filter(district_id=district_id).values("id", "name", "body_type")
#     return JsonResponse(list(lbs), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_wards(request, localbody_id):
#     """Load wards for a specific localbody"""
#     try:
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         # Convert to the format expected by the frontend
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# # Test endpoint without authentication for debugging
# def debug_wards_no_auth(request, localbody_id):
#     """Debug endpoint to test ward loading without authentication"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         print(f"DEBUG NO AUTH: Loading wards for localbody_id {localbody_id}")
#         print(f"DEBUG NO AUTH: Found {len(wards_data)} wards")
#         print(f"DEBUG NO AUTH: Sample data: {wards_data[:2] if wards_data else 'None'}")
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         print(f"DEBUG NO AUTH: Error: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates(request, localbody_id):
#     events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#     # FullCalendar expects events with at least id and start
#     data = [{"id": e["id"], "title": "Assigned", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates_by_ward(request, localbody_id):
#     """Get calendar dates filtered by ward number"""
#     ward_number = request.GET.get('ward')
#     if ward_number:
#         # For now, we'll return all calendar dates for the localbody
#         # In a more advanced implementation, you might have ward-specific calendar entries
#         events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#         data = [{"id": e["id"], "title": f"Assigned - Ward {ward_number}", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     else:
#         data = []
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def create_calendar_date(request, localbody_id):
#     """Create one date or range. Expects 'date' in YYYY-MM-DD or 'start' & 'end' for ranges."""
#     lb = get_object_or_404(LocalBody, pk=localbody_id)

#     # support single-date or start/end
#     start = request.POST.get("start")
#     end = request.POST.get("end")
#     single = request.POST.get("date")

#     created = []
#     if single:
#         d = parse_date(single)
#         if not d:
#             return HttpResponseBadRequest("Invalid date")
#         entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=d)
#         if created_flag:
#             created.append({"id": entry.id, "date": entry.date.isoformat()})
#         return JsonResponse({"status": "created", "created": created})

#     if start and end:
#         s = parse_date(start)
#         e = parse_date(end)
#         if not s or not e:
#             return HttpResponseBadRequest("Invalid start/end")
#         cur = s
#         while cur <= e:
#             entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=cur)
#             if created_flag:
#                 created.append({"id": entry.id, "date": entry.date.isoformat()})
#             cur += timedelta(days=1)
#         return JsonResponse({"status": "created_range", "created": created})

#     return HttpResponseBadRequest("Provide 'date' or 'start' and 'end'.")


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def update_calendar_date(request, pk):
#     """Change date for an existing LocalBodyCalendar entry. Expect 'new_date' YYYY-MM-DD"""
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     new_date_raw = request.POST.get("new_date")
#     if not new_date_raw:
#         return HttpResponseBadRequest("Missing new_date")
#     new_date = parse_date(new_date_raw.split("T")[0])
#     if not new_date:
#         return HttpResponseBadRequest("Invalid date")
#     # prevent duplicates: if another entry exists for that localbody on same date -> reject
#     exists = LocalBodyCalendar.objects.filter(localbody=entry.localbody, date=new_date).exclude(pk=entry.pk).exists()
#     if exists:
#         return JsonResponse({"status": "conflict", "message": "Date already assigned"}, status=409)
#     entry.date = new_date
#     entry.save()
#     return JsonResponse({"status": "updated", "id": entry.id, "date": entry.date.isoformat()})


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def delete_calendar_date(request, pk):
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     entry.delete()
#     return JsonResponse({"status": "deleted", "id": pk})






# # /////////////// super admin create waste oder


# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser
# from super_admin_dashboard.models import State, District, LocalBody
# @login_required
# def create_waste_profile(request):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     if request.method == "POST":
#         contact_number = request.POST.get("contact_number")

#         # Step 1: Check if customer exists
#         try:
#             customer = CustomUser.objects.get(contact_number=contact_number, role=0)
#         except CustomUser.DoesNotExist:
#             messages.error(request, "No registered customer found with this contact number.")
#             return redirect("super_admin_dashboard:create_waste_profile")

#         # Step 2: Collect waste info details from form
#         full_name = request.POST.get("full_name")
#         secondary_number = request.POST.get("secondary_number")
#         pickup_address = request.POST.get("pickup_address")
#         landmark = request.POST.get("landmark")
#         pincode = request.POST.get("pincode")
#         state_id = request.POST.get("state")
#         district_id = request.POST.get("district")
#         localbody_id = request.POST.get("localbody")
#         waste_type = request.POST.get("waste_type")
#         number_of_bags = request.POST.get("number_of_bags")
#         ward = request.POST.get("ward")
#         selected_date_id = request.POST.get("selected_date")  # calendar selected date

#         # Step 3: Create Waste Profile
#         waste_info = CustomerWasteInfo.objects.create(
#             user=customer,
#             full_name=full_name,
#             secondary_number=secondary_number,
#             pickup_address=pickup_address,
#             landmark=landmark,
#             pincode=pincode,
#             state_id=state_id,
#             district_id=district_id,
#             localbody_id=localbody_id,
#             waste_type=waste_type,
#             number_of_bags=number_of_bags,
#             ward=ward
#         )

#         # Step 4: Save pickup date if given
#         if selected_date_id:
#             try:
#                 cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                 CustomerPickupDate.objects.create(
#                     user=customer,
#                     waste_info=waste_info,
#                     localbody_calendar=cal
#                 )
#             except LocalBodyCalendar.DoesNotExist:
#                 messages.warning(request, "Invalid pickup date selected.")

#         messages.success(request, f"Waste profile created for {customer.first_name}")
#         return redirect("super_admin_dashboard:view_customer_waste_info")

#     # GET request
#     states = State.objects.all()
#     ward_range = range(1, 74)  # Wards 1–73
#     bag_range = range(1, 11)   # Bags 1–10
#     # For super admin form, we don't have a localbody selected yet, so show numbers only
#     ward_options = get_ward_options(None)

#     return render(request, "superadmin_waste_form.html", {
#         "states": states,
#         "ward_range": ward_range,
#         "bag_range": bag_range,
#         "ward_options": ward_options,
#     })




# from .forms import WasteProfileForm  # we'll create this form



# @login_required
# def view_waste_profile(request, pk):
#     waste_info = get_object_or_404(
#         CustomerWasteInfo.objects.select_related(
#             "user", "state", "district", "localbody", "assigned_collector"
#         ),
#         pk=pk
#     )

#     # pickup dates for this profile
#     pickup_dates = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     return render(request, "superadmin_view_waste.html", {
#         "info": waste_info,
#         "pickup_dates": pickup_dates,
#     })



# @login_required
# def edit_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     existing_pickups = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     if request.method == "POST":
#         form = WasteProfileForm(request.POST, instance=waste_info)
#         if form.is_valid():
#             waste_info = form.save()

#             selected_date_id = request.POST.get("selected_date")
#             if selected_date_id:
#                 try:
#                     cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                     CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={"localbody_calendar": cal}
#                     )
#                 except LocalBodyCalendar.DoesNotExist:
#                     messages.warning(request, "⚠️ Invalid pickup date selected.")

#             messages.success(request, "✅ Waste profile updated successfully.")
#             return redirect("super_admin_dashboard:waste_info_list")
#     else:
#         form = WasteProfileForm(instance=waste_info)

#     available_dates = LocalBodyCalendar.objects.filter(localbody=waste_info.localbody).order_by("date")
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {districts.count()}")
#     print(f"DEBUG: LocalBodies count: {localbodies.count()}")
#     print(f"DEBUG: Selected filters - District: {request.GET.get('district_filter')}, LocalBody: {request.GET.get('localbody_filter')}, Phone: {request.GET.get('phone_filter')}")

#     return render(request, "superadmin_edit_waste.html", {
#         "form": form,
#         "info": waste_info,
#         "existing_pickups": existing_pickups,
#         "available_dates": available_dates,
#         "districts": districts,
#         "localbodies": localbodies
#     })



# @login_required
# def delete_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     if request.method == "POST":
#         waste_info.delete()
#         messages.success(request, "🗑️ Waste profile deleted successfully.")
#         return redirect("super_admin_dashboard:waste_info_list")  # ✅ updated

#     return render(request, "superadmin_confirm_delete.html", {
#         "info": waste_info
#     })


# from django.core.paginator import Paginator
# from django.db.models import Q

# @login_required
# def waste_info_list(request):
#     search_query = request.GET.get("q", "")   # search input
#     page_number = request.GET.get("page", 1)  # current page

#     # Fetch all customer waste profiles
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         "state", "district", "localbody", "assigned_collector", "user"
#     ).prefetch_related("customerpickupdate_set__localbody_calendar")

#     # ✅ Search filter (name / phone / address)
#     if search_query:
#         waste_infos = waste_infos.filter(
#             Q(user__first_name__icontains=search_query) |
#             Q(user__last_name__icontains=search_query) |
#             Q(user__contact_number__icontains=search_query) |
#             Q(pickup_address__icontains=search_query)
#         )

#     # ✅ Pagination (10 profiles per page)
#     paginator = Paginator(waste_infos.order_by("-id"), 10)
#     page_obj = paginator.get_page(page_number)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     return render(request, "waste_info_list.html", {
#         "page_obj": page_obj,
#         "collectors": collectors,
#         "search_query": search_query,
#     })

# @login_required
# @user_passes_test(is_super_admin)
# def load_localbodies_for_reports(request):
#     district_id = request.GET.get('district_id')
#     localbodies = LocalBody.objects.filter(district_id=district_id).values("id", "name") if district_id else []
#     return JsonResponse(list(localbodies), safe=False)

# @login_required
# @user_passes_test(is_super_admin)
# def generate_reports(request):
#     """
#     View to display the reports page.
#     """
#     return render(request, 'reports.html')

# @login_required
# @user_passes_test(is_super_admin)
# def generate_report(request):
#     """Generate various types of reports"""
#     if request.method == 'POST':
#         try:
#             report_type = request.POST.get('report_type')
#             print(f"Generating report type: {report_type}")

#             # Get real data for reports
#             from customer_dashboard.models import CustomerWasteInfo
#             from authentication.models import CustomUser
#             from waste_collector_dashboard.models import WasteCollection
#             from datetime import date, datetime, timedelta

#             # Initialize report data
#             report_data = {
#                 'report_type': report_type,
#                 'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                 'report_name': f"{report_type.replace('_', ' ').title()} Report"
#             }

#             # Generate specific report data based on type
#             if report_type == 'daily_collection':
#                 # Get today's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date=today
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'collections_data': [{
#                         'customer': col.customer.get_full_name() if col.customer else 'Unknown',
#                         'address': col.location,
#                         'waste_type': col.customer.customerwasteinfo_set.first().waste_type if col.customer and col.customer.customerwasteinfo_set.exists() else 'Unknown',
#                         'bags': col.number_of_bags,
#                         'collected_at': col.collection_time.strftime('%H:%M') if col.collection_time else 'N/A'
#                     } for col in collections]
#                 })

#             elif report_type == 'weekly_collection':
#                 # Get this week's collections
#                 today = date.today()
#                 week_start = today - timedelta(days=today.weekday())
#                 week_end = week_start + timedelta(days=6)

#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__range=[week_start, week_end]
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
#                 })

#             elif report_type == 'monthly_collection':
#                 # Get this month's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__year=today.year,
#                     scheduled_date__month=today.month
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': today.strftime('%B %Y')
#                 })

#             elif report_type == 'customer_summary':
#                 # Get customer summary data
#                 customers = CustomUser.objects.filter(role=0)
#                 total_customers = customers.count()
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).count()

#                 report_data.update({
#                     'total_customers': total_customers,
#                     'active_customers': active_customers,
#                     'new_customers_this_month': active_customers
#                 })

#             elif report_type == 'active_customers':
#                 # Get active customers
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).select_related('user', 'state', 'district', 'localbody')

#                 report_data.update({
#                     'total_active_customers': active_customers.count(),
#                     'customer_list': [{
#                         'name': info.user.get_full_name() if info.user else 'Unknown',
#                         'phone': info.user.contact_number if hasattr(info.user, 'contact_number') else 'N/A',
#                         'address': info.pickup_address if hasattr(info, 'pickup_address') else 'N/A',
#                         'waste_type': info.waste_type,
#                         'status': info.status,
#                         'last_collection': 'N/A',
#                         'days_since_last': 'N/A'
#                     } for info in active_customers]
#                 })

#             elif report_type == 'payment_analysis':
#                 report_data.update({
#                     'payment_analysis': 'Payment analysis data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'outstanding_payments':
#                 report_data.update({
#                     'outstanding_payments': 'Outstanding payments data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'collector_performance':
#                 # Analyze collector performance
#                 collectors = CustomUser.objects.filter(role=1)
#                 performance_data = []

#                 for collector in collectors:
#                     try:
#                         # Get collections for this collector this month
#                         collector_collections = WasteCollection.objects.filter(
#                             collector=collector,
#                             scheduled_date__month=date.today().month,
#                             scheduled_date__year=date.today().year
#                         )

#                         total_collections = collector_collections.count()
#                         total_bags = sum(col.number_of_bags for col in collector_collections)

#                         performance_data.append({
#                             'collector_name': collector.get_full_name(),
#                             'total_collections': total_collections,
#                             'total_bags': total_bags,
#                             'days_worked': len(set(col.scheduled_date for col in collector_collections if col.scheduled_date)),
#                         })
#                     except Exception as e:
#                         print(f"Error processing collector {collector.id}: {e}")
#                         continue

#                 # Sort by performance
#                 performance_data.sort(key=lambda x: x['total_collections'], reverse=True)

#                 report_data.update({
#                     'period': date.today().strftime('%B %Y'),
#                     'total_collectors': len(collectors),
#                     'performance_data': performance_data,
#                     'top_performers': performance_data[:5]
#                 })

#             elif report_type == 'efficiency_metrics':
#                 report_data.update({
#                     'efficiency_metrics': 'Operational efficiency metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'service_level':
#                 report_data.update({
#                     'service_level': 'Service level metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             else:
#                 return JsonResponse({'success': False, 'error': f'Unknown report type: {report_type}'}, status=400)

#             print("Report generated successfully:", report_data)
#             return JsonResponse({
#                 'success': True,
#                 'report_data': report_data,
#                 'report_name': report_data['report_name']
#             })

#         except Exception as e:
#             error_msg = str(e)
#             print("Error generating report:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# @login_required
# @user_passes_test(is_super_admin)
# def load_districts_for_reports(request):
#     state_id = request.GET.get('state_id')
#     districts = District.objects.filter(state_id=state_id).values("id", "name") if state_id else []
#     return JsonResponse(list(districts), safe=False)


#   # Get additional data for CRUD functionality
#     from authentication.models import CustomUser
#     from super_admin_dashboard.models import LocalBody

#     all_customers = CustomUser.objects.filter(role=0)  # Customers
#     all_localbodies = LocalBody.objects.all()

#     try:
#         response = render(request, 'view_collected_data.html', {
#             'all_data': all_data,
#             'all_customers': all_customers,
#             'all_localbodies': all_localbodies,
#         })
#         print("Template rendered successfully")
#         print("=======================================")
#         return response
#     except Exception as e:
#         print(f"ERROR rendering template: {e}")
#         import traceback
#         traceback.print_exc()
#         raise


# # CRUD Operations for Waste Collection
# @login_required
# @user_passes_test(can_view_collected_data)
# def update_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)

#         # Update fields based on POST data
#         waste_collection.ward = request.POST.get('ward', waste_collection.ward)
#         waste_collection.location = request.POST.get('location', waste_collection.location)
#         waste_collection.number_of_bags = request.POST.get('number_of_bags', waste_collection.number_of_bags)
#         waste_collection.building_no = request.POST.get('building_no', waste_collection.building_no)
#         waste_collection.street_name = request.POST.get('street_name', waste_collection.street_name)
#         waste_collection.kg = request.POST.get('kg', waste_collection.kg)

#         # Handle customer and localbody foreign keys
#         if request.POST.get('customer'):
#             customer_id = int(request.POST.get('customer'))
#             waste_collection.customer = CustomUser.objects.get(id=customer_id, role=0)

#         if request.POST.get('localbody'):
#             localbody_id = int(request.POST.get('localbody'))
#             waste_collection.localbody = LocalBody.objects.get(id=localbody_id)

#         # Handle date fields
#         scheduled_date_str = request.POST.get('scheduled_date')
#         if scheduled_date_str:
#             waste_collection.scheduled_date = scheduled_date_str
#         elif scheduled_date_str == '':
#             waste_collection.scheduled_date = None

#         # Handle time field
#         collection_time_str = request.POST.get('collection_time')
#         if collection_time_str:
#             from datetime import datetime
#             time_obj = datetime.strptime(collection_time_str, '%H:%M').time()
#             waste_collection.collection_time = time_obj
#         elif collection_time_str == '':
#             waste_collection.collection_time = None

#         # Recalculate total amount if kg or rate changes
#         waste_collection.save()

#         return JsonResponse({'success': True, 'message': 'Record updated successfully'})

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected customer does not exist'})
#     except LocalBody.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected local body does not exist'})
#     except ValueError as e:
#         return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})


# @login_required
# @user_passes_test(can_view_collected_data)
# def delete_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)
#         waste_collection.delete()
#         return JsonResponse({'success': True, 'message': 'Record deleted successfully'})

#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})







# @login_required
# @user_passes_test(is_super_admin)
# def export_all_users_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"all_users_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Role', 'Contact Number', 'Date Joined'])

#     users = CustomUser.objects.all().order_by('id')

#     for user in users:
#         writer.writerow([
#             user.id,
#             user.username,
#             user.first_name,
#             user.last_name,
#             user.email,
#             user.get_role_display(),
#             user.contact_number,
#             user.date_joined.strftime("%Y-%m-%d %H:%M") if user.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_customers_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"customers_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     customers = CustomUser.objects.filter(role=0)

#     for customer in customers:
#         writer.writerow([
#             customer.id,
#             customer.username,
#             customer.first_name,
#             customer.last_name,
#             customer.email,
#             customer.contact_number,
#             customer.date_joined.strftime("%Y-%m-%d %H:%M") if customer.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_collectors_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"collectors_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     collectors = CustomUser.objects.filter(role=1)

#     for collector in collectors:
#         writer.writerow([
#             collector.id,
#             collector.username,
#             collector.first_name,
#             collector.last_name,
#             collector.email,
#             collector.contact_number,
#             collector.date_joined.strftime("%Y-%m-%d %H:%M") if collector.date_joined else 'N/A'
#         ])

#     return response


# # Test endpoint for debugging with authentication
# @login_required
# @user_passes_test(is_super_admin)
# def test_wards_endpoint(request, localbody_id):
#     """Test endpoint to verify ward loading is working"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse({
#             "status": "success",
#             "localbody_id": localbody_id,
#             "localbody_name": localbody.name,
#             "ward_count": len(data),
#             "wards": data
#         })
#     except LocalBody.DoesNotExist:
#         return JsonResponse({
#             "status": "error",
#             "message": "Local body not found"
#         }, status=404)
#     except Exception as e:
#         return JsonResponse({
#             "status": "error",
#             "message": str(e)
#         }, status=500)


# # Price Control Views
# @login_required
# @user_passes_test(is_super_admin)
# def price_control(request):
#     """Price control page for managing waste collection pricing"""
#     from .models import District, LocalBody, WasteTypePrice, ServiceFee, LocationPriceMultiplier, PriceControl

#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.select_related('district').all().order_by('name')

#     # Simple in-page data for Area Price Control dropdowns (no AJAX)
#     localbodies_data = [
#         {"id": lb.id, "name": lb.name or "", "district_id": lb.district_id, "body_type_display": lb.get_body_type_display()}
#         for lb in localbodies
#     ]
#     wards_by_lb = {str(lb.id): [{"ward_number": str(o[0]), "ward_name": o[1] or "Ward " + str(o[0])} for o in get_ward_options(lb.name)] for lb in localbodies}

#     # Get existing pricing data
#     waste_prices = WasteTypePrice.objects.all()
#     service_fee = ServiceFee.objects.first()
#     location_multipliers = LocationPriceMultiplier.objects.select_related('district', 'localbody').all()
#     area_prices = PriceControl.objects.select_related('district', 'localbody').all()

#     context = {
#         'districts': districts,
#         'localbodies': localbodies,
#         'localbodies_data': localbodies_data,
#         'wards_by_localbody': wards_by_lb,
#         'waste_prices': waste_prices,
#         'service_fee': service_fee,
#         'location_multipliers': location_multipliers,
#         'area_prices': area_prices,
#     }
#     return render(request, 'price_control.html', context)


# @login_required
# @user_passes_test(is_super_admin)
# def load_price_history(request):
#     """Load price history for display"""
#     if request.method == 'GET':
#         try:
#             from .models import PriceHistory
#             from django.core.serializers.json import DjangoJSONEncoder

#             history = PriceHistory.objects.select_related('updated_by').order_by('-created_at')[:20]

#             history_data = []
#             for item in history:
#                 history_data.append({
#                     'date': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                     'type': item.pricing_type.replace('_', ' ').title(),
#                     'category': item.category,
#                     'old_price': f"₹{item.old_value}" if item.old_value else '-',
#                     'new_price': f"₹{item.new_value}" if item.new_value else '-',
#                     'updated_by': item.updated_by.get_full_name() if item.updated_by else 'System',
#                     'status': 'active' if item.action_type == 'create' else 'updated'
#                 })

#             return JsonResponse({
#                 'success': True,
#                 'data': history_data
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_waste_price(request):
#     """Save waste type pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import WasteTypePrice, PriceHistory
#             data = json.loads(request.body)

#             waste_type = data.get('waste_type')
#             price_per_kg = data.get('price_per_kg')
#             status = data.get('status', 'active')

#             # Validate input
#             if not waste_type or price_per_kg is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             price_per_kg = float(price_per_kg)
#             if price_per_kg < 0:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price must be non-negative'
#                 })

#             # Get or create waste type price
#             waste_price, created = WasteTypePrice.objects.get_or_create(
#                 waste_type=waste_type,
#                 defaults={
#                     'price_per_kg': price_per_kg,
#                     'status': status,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_price = waste_price.price_per_kg
#                 waste_price.price_per_kg = price_per_kg
#                 waste_price.status = status
#                 waste_price.updated_by = request.user
#                 waste_price.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     old_value=old_price,
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Waste type price saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_service_fees(request):
#     """Save service fee pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import ServiceFee, PriceHistory
#             data = json.loads(request.body)

#             base_fee = data.get('base_fee')
#             fee_per_bag = data.get('fee_per_bag')
#             min_charge = data.get('min_charge')

#             # Validate input
#             if base_fee is None or fee_per_bag is None or min_charge is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             base_fee = float(base_fee)
#             fee_per_bag = float(fee_per_bag)
#             min_charge = float(min_charge)

#             if any(x < 0 for x in [base_fee, fee_per_bag, min_charge]):
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'All fees must be non-negative'
#                 })

#             # Get or create service fee
#             service_fee, created = ServiceFee.objects.get_or_create(
#                 pk=1,  # Assume single service fee record
#                 defaults={
#                     'base_fee': base_fee,
#                     'fee_per_bag': fee_per_bag,
#                     'min_charge': min_charge,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_base_fee = service_fee.base_fee
#                 old_fee_per_bag = service_fee.fee_per_bag
#                 old_min_charge = service_fee.min_charge

#                 service_fee.base_fee = base_fee
#                 service_fee.fee_per_bag = fee_per_bag
#                 service_fee.min_charge = min_charge
#                 service_fee.updated_by = request.user
#                 service_fee.save()

#                 # Log changes to history
#                 if old_base_fee != base_fee:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Base Fee',
#                         old_value=old_base_fee,
#                         new_value=base_fee,
#                         updated_by=request.user
#                     )

#                 if old_fee_per_bag != fee_per_bag:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Fee per Bag',
#                         old_value=old_fee_per_bag,
#                         new_value=fee_per_bag,
#                         updated_by=request.user
#                     )

#                 if old_min_charge != min_charge:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Minimum Charge',
#                         old_value=old_min_charge,
#                         new_value=min_charge,
#                         updated_by=request.user
#                     )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='service_fee',
#                     category='Service Fees',
#                     new_value=base_fee,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Service fees saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_location_multiplier(request):
#     """Save location-based price multiplier"""
#     if request.method == 'POST':
#         try:
#             from .models import LocationPriceMultiplier, PriceHistory, District, LocalBody
#             data = json.loads(request.body)

#             # Validate price multiplier
#             price_multiplier = float(data.get('price_multiplier', 0))
#             if price_multiplier > 500.0 or price_multiplier < 0.1:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price multiplier must be between 0.1 and 500.0'
#                 })

#             district_id = data.get('district')
#             localbody_id = data.get('localbody')

#             if not district_id or not localbody_id:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'District and Local Body are required'
#                 })

#             # Get district and localbody objects
#             district = District.objects.get(id=district_id)
#             localbody = LocalBody.objects.get(id=localbody_id)

#             # Get or create location price multiplier
#             location_multiplier, created = LocationPriceMultiplier.objects.get_or_create(
#                 district=district,
#                 localbody=localbody,
#                 defaults={
#                     'price_multiplier': price_multiplier,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_multiplier = location_multiplier.price_multiplier
#                 location_multiplier.price_multiplier = price_multiplier
#                 location_multiplier.updated_by = request.user
#                 location_multiplier.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     old_value=old_multiplier,
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Location multiplier saved successfully'
#             })
#         except ValueError:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid price multiplier value'
#             })
#         except District.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'District not found'
#             })
#         except LocalBody.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Local Body not found'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})






# @login_required
# def customer_activity_details(request, customer_id):
#     """
#     Show detailed customer activity including waste info and collection history
#     """
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     from waste_collector_dashboard.models import WasteCollection
#     from django.db.models import Q, Sum

#     # Get the customer user
#     try:
#         customer = CustomUser.objects.get(id=customer_id, role=0)
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Customer not found')
#         return redirect('super_admin_dashboard:view_customer_waste_info')

#     # Get customer waste info
#     waste_infos = CustomerWasteInfo.objects.filter(
#         user=customer
#     ).select_related(
#         'state', 'district', 'localbody', 'assigned_collector'
#     ).order_by('-created_at')

#     # Get collection history for this customer
#     collection_history = WasteCollection.objects.filter(
#         customer=customer
#     ).select_related(
#         'collector', 'localbody'
#     ).order_by('-created_at')

#     # Get pickup dates
#     pickup_dates = CustomerPickupDate.objects.filter(
#         user=customer
#     ).select_related(
#         'localbody_calendar', 'waste_info'
#     ).order_by('-created_at')

#     # Calculate statistics
#     total_collections = collection_history.count()
#     total_kg_collected = collection_history.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     total_amount_paid = collection_history.aggregate(
#         total_amount=Sum('total_amount')
#     )['total_amount'] or 0

#     # Recent activity (last 10 items from both waste info and collections)
#     recent_waste_info = waste_infos[:5]
#     recent_collections = collection_history[:5]

#     context = {
#         'customer': customer,
#         'waste_infos': waste_infos,
#         'collection_history': collection_history,
#         'pickup_dates': pickup_dates,
#         'total_collections': total_collections,
#         'total_kg_collected': total_kg_collected,
#         'total_amount_paid': total_amount_paid,
#         'recent_waste_info': recent_waste_info,
#         'recent_collections': recent_collections,
#     }

#     return render(request, 'customer_activity_details.html', context)


# @login_required
# def collector_activity_details(request, collector_id):
#     """
#     Show detailed collector activity including collection history and assigned customers
#     """
#     from customer_dashboard.models import CustomerWasteInfo
#     from waste_collector_dashboard.models import WasteCollection
#     from django.db.models import Q, Sum, Count

#     # Get the collector user
#     try:
#         collector = CustomUser.objects.get(id=collector_id, role=1)
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Collector not found')
#         return redirect('super_admin_dashboard:view_collected_data')

#     # Get collection history for this collector
#     collection_history = WasteCollection.objects.filter(
#         collector=collector
#     ).select_related(
#         'customer', 'localbody'
#     ).order_by('-created_at')

#     # Get assigned customers to this collector
#     assigned_customers = CustomerWasteInfo.objects.filter(
#         assigned_collector=collector
#     ).select_related(
#         'user', 'state', 'district', 'localbody'
#     ).order_by('-created_at')

#     # Calculate statistics
#     total_collections = collection_history.count()
#     total_kg_collected = collection_history.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     total_amount_collected = collection_history.aggregate(
#         total_amount=Sum('total_amount')
#     )['total_amount'] or 0

#     total_customers_assigned = assigned_customers.count()

#     # Recent activity
#     recent_collections = collection_history[:10]
#     recent_assigned_customers = assigned_customers[:5]

#     # Payment method statistics
#     payment_stats = collection_history.values('payment_method').annotate(
#         count=Count('id')
#     ).order_by('-count')

#     context = {
#         'collector': collector,
#         'collection_history': collection_history,
#         'assigned_customers': assigned_customers,
#         'total_collections': total_collections,
#         'total_kg_collected': total_kg_collected,
#         'total_amount_collected': total_amount_collected,
#         'total_customers_assigned': total_customers_assigned,
#         'recent_collections': recent_collections,
#         'recent_assigned_customers': recent_assigned_customers,
#         'payment_stats': payment_stats,
#     }

#     return render(request, 'collector_activity_details.html', context)




#  # --- Notifications for super admin dashboard (latest admin_home) ---
#     from datetime import timedelta
#     cutoff_date = timezone.now() - timedelta(days=60)
#     Notification.objects.filter(user=request.user, created_at__lt=cutoff_date).delete()

#     # Pending orders notification
#     Notification.create_pending_order_notification(
#         user=request.user,
#         order_count=pending_orders,
#     )

#     # Collection rate notification
#     Notification.create_collection_rate_notification(
#         user=request.user,
#         rate=collection_rate
#     )

#     # Milestone notification when completed orders reach certain thresholds
#     if completed_orders >= 50:
#         milestone_title = "50+ Orders Completed"
#         description = f"You have successfully completed {completed_orders} waste collection orders."
#         if not Notification.objects.filter(
#             user=request.user,
#             title__icontains=milestone_title
#         ).exists():
#             Notification.create_milestone_notification(
#                 user=request.user,
#                 milestone_title=milestone_title,
#                 description=description
#             )

#     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]










# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render, redirect,get_object_or_404
# from django.http import JsonResponse
# from authentication.models import CustomUser
# from waste_collector_dashboard.models import WasteCollection
# # from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate  # Moved inside functions to avoid circular import
# from django.contrib import messages
# from .utils import is_super_admin
# from django.template.loader import get_template, render_to_string
# from django.utils import timezone
# from django.db.models import Sum
# from datetime import datetime
# from .models import State, District, LocalBody, LocalBodyCalendar, CollectorServiceArea

# def get_ward_names():
#     """Return a dictionary mapping ward numbers to ward names"""
#     return {
#         1: "Fort Kochi",
#         2: "Kalvathy",
#         3: "Earavely",
#         4: "Karippalam",
#         5: "Cheralayi",
#         6: "Mattanchery",
#         7: "Chakkamadam",
#         8: "Karuvelippady",
#         9: "Island North",
#         10: "Ravipuram",
#         11: "Ernakulam South",
#         12: "Gandhi Nagar",
#         13: "Kathrikadavu",
#         14: "Ernakulam Central",
#         15: "Ernakulam North",
#         16: "Kaloor South",
#         17: "Kaloor North",
#         18: "Thrikkanarvattom",
#         19: "Ayyappankavu",
#         20: "Pottakuzhy",
#         21: "Elamakkara South",
#         22: "Pachalam",
#         23: "Thattazham",
#         24: "Vaduthala West",
#         25: "Vaduthala East",
#         26: "Elamakkara North",
#         27: "Puthukkalavattam",
#         28: "Kunnumpuram",
#         29: "Ponekkara",
#         30: "Edappally",
#         31: "Changampuzha",
#         32: "Dhevankulangara",
#         33: "Palarivattom",
#         34: "Stadium",
#         35: "Karanakkodam",
#         36: "Puthiyaroad",
#         37: "Padivattam",
#         38: "Vennala",
#         39: "Chakkaraparambu",
#         40: "Chalikkavattam",
#         41: "Thammanam",
#         42: "Elamkulam",
#         43: "Girinagar",
#         44: "Ponnurunni",
#         45: "Ponnurunni East",
#         46: "Vyttila",
#         47: "Poonithura",
#         48: "Vyttila Janatha",
#         49: "Kadavanthra",
#         50: "Panampilly Nagar",
#         51: "Perumanoor",
#         52: "Konthuruthy",
#         53: "Thevara",
#         54: "Island South",
#         55: "Kadebhagam",
#         56: "Palluruthy East",
#         57: "Thazhuppu",
#         58: "Eadakochi North",
#         59: "Edakochi South",
#         60: "Perumbadappu",
#         61: "Konam",
#         62: "Palluruthy Kacheripady",
#         63: "Nambyapuram",
#         64: "Palluruthy",
#         65: "Pullardesam",
#         66: "Tharebhagam",
#         67: "Thoppumpady",
#         68: "Mundamvely East",
#         69: "Mundamvely",
#         70: "Manassery",
#         71: "Moolamkuzhy",
#         72: "Chullickal",
#         73: "Nasrathu",
#         74: "Panayappilly",
#         75: "Amaravathy",
#         76: "Fortkochi Veli"
#     }

# def get_ward_options(localbody_name=None):
#     """Kochi/Ernakulam → 76 named wards (Fort Kochi, etc.); other local bodies → Ward 1 to Ward 10."""
#     ward_names = get_ward_names()
#     name_lower = (localbody_name or '').lower()
#     if name_lower and ('kochi' in name_lower or 'ernakulam' in name_lower):
#         return [(i, ward_names.get(i, f'Ward {i}')) for i in range(1, 77)]
#     return [(i, f'Ward {i}') for i in range(1, 11)]


# @login_required
# def admin_home(request):
#     from customer_dashboard.models import CustomerPickupDate, CustomerWasteInfo
#     from django.db.models import Count, Q

#     # Get current date info
#     now = timezone.now()
#     first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

#     # Calculate statistics
#     total_customers = CustomUser.objects.filter(role=0).count()
#     total_collectors = CustomUser.objects.filter(role=1).count()

#     # Collections this month
#     monthly_collections = WasteCollection.objects.filter(
#         created_at__gte=first_day_of_month
#     ).count()

#     # Total waste collected (sum of kg)
#     total_waste_collected_data = WasteCollection.objects.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     # 1. Collection Rate: Collections vs Scheduled Pickups
#     scheduled_pickups = CustomerPickupDate.objects.filter(
#         localbody_calendar__date__gte=first_day_of_month.date(),
#         localbody_calendar__date__lte=now.date()
#     ).count()

#     collection_rate = 0
#     if scheduled_pickups > 0:
#         collection_rate = min(100, int((monthly_collections / scheduled_pickups) * 100))
#     elif monthly_collections > 0:
#         collection_rate = 100

#     # 2. Customer Satisfaction: Based on "On-Time" collections
#     # If scheduled_date == collection_date or matches within 1 day
#     on_time_collections = 0
#     total_with_schedule = 0
#     collections_with_schedule = WasteCollection.objects.filter(
#         scheduled_date__isnull=False,
#         created_at__gte=first_day_of_month
#     )

#     for coll in collections_with_schedule:
#         total_with_schedule += 1
#         # Compare created_at date with scheduled_date
#         collection_date = coll.created_at.date()
#         scheduled_date = coll.scheduled_date

#         # Ensure we are comparing date to date (scheduled_date might be datetime in some cases)
#         if hasattr(scheduled_date, 'date'):
#             scheduled_date = scheduled_date.date()

#         if collection_date <= scheduled_date:
#             on_time_collections += 1

#     customer_satisfaction = 4.5 # Default high starting point
#     if total_with_schedule > 0:
#         satisfaction_ratio = on_time_collections / total_with_schedule
#         customer_satisfaction = round(3.0 + (satisfaction_ratio * 2.0), 1) # Scale between 3.0 and 5.0

#     # 3. Recycling Rate: Estimated based on waste types
#     # Check CustomerWasteInfo for recyclable types
#     recyclable_keywords = ['plastic', 'paper', 'metal', 'glass', 'can', 'bottle', 'recyclable']
#     recyclable_query = Q()
#     for kw in recyclable_keywords:
#         recyclable_query |= Q(waste_type__icontains=kw)

#     total_profiles = CustomerWasteInfo.objects.count()
#     recyclable_profiles = CustomerWasteInfo.objects.filter(recyclable_query).count()

#     recycling_rate = 0
#     if total_profiles > 0:
#         recycling_rate = int((recyclable_profiles / total_profiles) * 100)
#     else:
#         recycling_rate = 65 # Reasonable industry average placeholder if no data

#     # Get order data for control all orders functionality
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'user', 'state', 'district', 'localbody', 'assigned_collector'
#     ).all()

#     total_orders = waste_infos.count()
#     pending_orders = waste_infos.filter(status='pending').count()
#     confirmed_orders = waste_infos.filter(status='in_progress').count()
#     completed_orders = waste_infos.filter(status='completed').count()

#     # Get all collectors for dropdown
#     collectors = CustomUser.objects.filter(role=1)

#     # Build orders data from real CustomerWasteInfo
#     orders = []
#     for info in waste_infos[:20]:  # Limit to first 20 orders
#         try:
#             # Get scheduled date for this waste info
#             pickup_date = info.customerpickupdate_set.select_related('localbody_calendar').first()
#             scheduled_date_order = pickup_date.localbody_calendar.date.strftime('%Y-%m-%d') if pickup_date and pickup_date.localbody_calendar else 'Not Scheduled'

#             # Get assigned collector name
#             collector_name = info.assigned_collector.get_full_name() if info.assigned_collector else 'Unassigned'

#             # Convert status to readable format
#             status_map = {
#                 'pending': 'Pending',
#                 'in_progress': 'In Progress',
#                 'completed': 'Completed',
#                 'collected': 'Collected'
#             }
#             readable_status = status_map.get(info.status, info.status)

#             order = {
#                 'id': info.id,
#                 'customer_name': info.full_name,
#                 'customer_phone': info.user.contact_number,
#                 'address': info.pickup_address,
#                 'waste_type': info.waste_type,
#                 'bags': info.number_of_bags or 0,
#                 'booking_date': info.created_at.strftime('%Y-%m-%d'),
#                 'scheduled_date': scheduled_date_order,
#                 'status': readable_status,
#                 'assigned_collector': collector_name,
#                 'ward': info.ward,
#                 'localbody': info.localbody.name if info.localbody else 'Not Assigned'
#             }
#             orders.append(order)
#         except Exception as e:
#             print(f"Error processing order {info.id}: {e}")
#             continue

#     context = {
#         'total_customers': total_customers,
#         'total_collectors': total_collectors,
#         'monthly_collections': monthly_collections,
#         'total_waste_collected': f"{total_waste_collected_data:.1f} KG",
#         'collection_rate': collection_rate,
#         'customer_satisfaction': customer_satisfaction,
#         'recycling_rate': recycling_rate,
#         'orders': orders,
#         'total_orders': total_orders,
#         'pending_orders': pending_orders,
#         'confirmed_orders': confirmed_orders,
#         'completed_orders': completed_orders,
#         'collectors': collectors
#     }

#     return render(request, 'super_admin_dashboard.html', context)


# @login_required
# def manage_order(request, order_id):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     # Add logging for debugging
#     print(f"manage_order called with order_id: {order_id}, method: {request.method}")
#     print(f"User authenticated: {request.user.is_authenticated}")
#     print(f"User: {request.user}")

#     if request.method == 'POST':
#         try:
#             action = request.POST.get('action')
#             print(f"Action: {action}")

#             # Get the waste info object
#             waste_info = CustomerWasteInfo.objects.get(id=order_id)
#             print(f"Waste info found: {waste_info.id}")

#             # Handle order management actions
#             if action == 'assign_collector':
#                 collector_id = request.POST.get('collector_id')
#                 print(f"Assigning collector: {collector_id}")
#                 if collector_id:
#                     collector = CustomUser.objects.get(id=collector_id, role=1)  # role=1 for collectors
#                     waste_info.assigned_collector = collector
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} assigned to collector successfully')
#                     print("Collector assigned successfully")

#             elif action == 'update_status':
#                 new_status = request.POST.get('status')
#                 print(f"Updating status to: {new_status}")
#                 if new_status in ['pending', 'in_progress', 'completed', 'collected']:
#                     waste_info.status = new_status
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} status updated to {new_status}')
#                     print("Status updated successfully")

#             elif action == 'reschedule':
#                 new_date = request.POST.get('new_date')
#                 print(f"Rescheduling to: {new_date}")
#                 if new_date:
#                     # First get or create the calendar entry if it doesn't exist
#                     calendar_entry, created = LocalBodyCalendar.objects.get_or_create(
#                         localbody=waste_info.localbody,
#                         date=new_date
#                     )
#                     # Update the scheduled date by creating/updating the CustomerPickupDate
#                     pickup_date, created = CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={'localbody_calendar': calendar_entry}
#                     )
#                     messages.success(request, f'Order {order_id} rescheduled to {new_date}')
#                     print("Order rescheduled successfully")

#             response_data = {'success': True}
#             print("Returning success response:", response_data)
#             return JsonResponse(response_data)

#         except CustomerWasteInfo.DoesNotExist:
#             error_msg = f'Order {order_id} not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except CustomUser.DoesNotExist:
#             error_msg = 'Collector not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except LocalBodyCalendar.DoesNotExist:
#             error_msg = 'Schedule date not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except Exception as e:
#             error_msg = str(e)
#             print("Unexpected error:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     # If not POST method
#     error_msg = 'Invalid request method'
#     print("Error:", error_msg)
#     return JsonResponse({'success': False, 'error': error_msg}, status=405)


# @login_required
# def user_list_view(request):
#     customers = CustomUser.objects.filter(role=0)
#     collectors = CustomUser.objects.filter(role=1)
#     admins = CustomUser.objects.filter(role=2)

#     return render(request, 'user_list.html', {
#         'customers': customers,
#         'collectors': collectors,
#         'admins': admins,
#     })
# @login_required
# def view_customers(request):
#     customers = CustomUser.objects.filter(role=0)
#     return render(request, 'view_customers.html', {'customers': customers})

# @login_required
# def view_waste_collectors(request):
#     collectors = CustomUser.objects.filter(role=1)
#     total_collectors = collectors.count()
#     service_areas = CollectorServiceArea.objects.select_related(
#         'collector', 'district', 'localbody'
#     ).order_by('collector__username', 'district__name', 'localbody__name')
#     # Same as view_collected_data: all districts and localbodies for dropdowns
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')
#     # Ward dropdown: use dedicated collectors endpoint (same app, login only)
#     from django.urls import reverse
#     try:
#         load_wards_url = request.build_absolute_uri(
#             reverse('adminpanel:load_wards_collectors', args=[0])
#         ).replace('/0/', '/')
#     except Exception:
#         load_wards_url = request.build_absolute_uri('/admin/users/collectors/load-wards/')
#     return render(request, 'view_collectors.html', {
#         'collectors': collectors,
#         'total_collectors': total_collectors,
#         'service_areas': service_areas,
#         'districts': districts,
#         'localbodies': localbodies,
#         'load_wards_url': load_wards_url,
#     })


# @login_required
# def assign_collector_service_area(request):
#     """Assign a service area (District, Local Body, Ward) to a waste collector."""
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
#     collector_id = request.POST.get('collector_id')
#     district_id = request.POST.get('district_id')
#     localbody_id = request.POST.get('localbody_id')
#     ward = request.POST.get('ward', '').strip()
#     if not all([collector_id, district_id, localbody_id, ward]):
#         return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
#     collector = get_object_or_404(CustomUser, id=collector_id, role=1)
#     district = get_object_or_404(District, id=district_id)
#     localbody = get_object_or_404(LocalBody, id=localbody_id)
#     if localbody.district_id != district.id:
#         return JsonResponse({'success': False, 'error': 'Local body does not belong to selected district'}, status=400)
#     obj, created = CollectorServiceArea.objects.get_or_create(
#         collector=collector,
#         district=district,
#         localbody=localbody,
#         ward=ward,
#     )
#     if created:
#         messages.success(request, f'Service area {district.name} / {localbody.name} / {ward} assigned to {collector.username}')
#     else:
#         messages.info(request, 'This service area is already assigned to this collector')
#     return redirect('adminpanel:view_collectors')


# @login_required
# def remove_collector_service_area(request, pk):
#     """Remove a service area assignment from a collector."""
#     if request.method != 'POST':
#         return redirect('adminpanel:view_collectors')
#     area = get_object_or_404(CollectorServiceArea, pk=pk)
#     area.delete()
#     messages.success(request, 'Service area assignment removed')
#     return redirect('adminpanel:view_collectors')


# @login_required
# def load_wards_collectors(request, localbody_id):
#     """Load wards for view_collectors page - only requires login"""
#     try:
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse([], safe=False)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# def load_localbodies_collectors(request, district_id):
#     """Load local bodies for view_collectors page - only requires login"""
#     try:
#         lbs = LocalBody.objects.filter(district_id=district_id).values("id", "name", "body_type")
#         return JsonResponse(list(lbs), safe=False)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# def view_super_admin(request):
#     super_admin = CustomUser.objects.filter(role=2)
#     return render(request, "view_super_admin.html", {"super_admin":super_admin})

# @login_required
# def view_admins(request):
#     admins = CustomUser.objects.filter(role=3)
#     return render(request, "view_admins.html", {"admins":admins})

# # \\\\\\\\\\\\\\\\\\\\\\\\\\\ user view //////////////////////

# from .forms import UserForm

# @login_required
# def user_list(request):
#     users = CustomUser.objects.all()
#     return render(request, "users_list.html", {"users": users})





# @login_required
# def user_create(request):
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Encrypt password before saving
#                 user.set_password(password)
#             else:  # Default password if none provided
#                 user.set_password("default123")
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm()
#     return render(request, 'user_form.html', {'form': form})

# # Update User
# @login_required
# def user_update(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == 'POST':
#         form = UserForm(request.POST, instance=user)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Reset password if admin entered new one
#                 user.set_password(password)
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm(instance=user)
#     return render(request, 'user_form.html', {'form': form, 'user': user})






# # Delete user
# @login_required
# def user_delete(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         user.delete()
#         messages.success(request, "User deleted successfully")
#         return redirect("super_admin_dashboard:users_list")
#     return render(request, "user_confirm_delete.html", {"user": user})



# from django.shortcuts import render
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser

# @login_required
# def view_customer_wasteinfo(request):
#     # Fetch only unassigned customer waste profiles with related fields
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'state', 'district', 'localbody', 'assigned_collector', 'user'
#     ).filter(assigned_collector__isnull=True)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     # Map waste_info_id → pickup date
#     pickup_dates = {}
#     pickups = CustomerPickupDate.objects.select_related('localbody_calendar', 'waste_info').all()
#     for pickup in pickups:
#         if pickup.waste_info:
#             pickup_dates[pickup.waste_info.id] = pickup.localbody_calendar.date

#     return render(request, 'view_customer_wasteinfo.html', {
#         'waste_infos': waste_infos,
#         'collectors': collectors,
#         'pickup_dates': pickup_dates,
#     })

# # Assign a waste collector to a CustomerWasteInfo entry
# @login_required
# def assign_waste_collector(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)
#     if request.method == 'POST':
#         collector_id = request.POST.get('collector')
#         collector = get_object_or_404(CustomUser, pk=collector_id, role=1)

#         # Store customer info for success message
#         customer_name = waste_info.user.username
#         customer_address = waste_info.pickup_address

#         # Assign collector and ensure is_collected is False so it appears in assigned customers list
#         waste_info.assigned_collector = collector
#         waste_info.is_collected = False  # Mark as not collected so collector can see it
#         waste_info.save()

#         messages.success(request, f"Customer {customer_name} at {customer_address} has been assigned to {collector.username}. The customer now appears in the collector's assigned customers list.")
#         return redirect('super_admin_dashboard:view_customer_waste_info')

#     collectors = CustomUser.objects.filter(role=1)
#     return render(request, 'assign_waste_collector.html', {
#         'waste_info': waste_info,
#         'collectors': collectors,
#     })


# #waste collector collect details from customer

# def can_view_collected_data(user):
#     # Role 1 is Collector, Role 2 is Super Admin
#     return user.is_authenticated and (getattr(user, 'role', None) in [1, 2] or user.is_superuser)

# @login_required
# @user_passes_test(can_view_collected_data)
# def view_collected_data(request):
#     # Get waste collection data with related information
#     user_role = getattr(request.user, 'role', None)
#     try:
#         user_role = int(user_role)
#     except (TypeError, ValueError):
#         user_role = None

#     # Get filter parameters
#     district_filter = request.GET.get('district')
#     localbody_filter = request.GET.get('localbody')
#     phone_filter = request.GET.get('phone')
#     from_date_filter = request.GET.get('from_date')
#     to_date_filter = request.GET.get('to_date')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {District.objects.count()}")
#     print(f"DEBUG: LocalBodies count: {LocalBody.objects.count()}")
#     print(f"DEBUG: Selected filters - District: {district_filter}, LocalBody: {localbody_filter}, Phone: {phone_filter}")

#     # Base queryset
#     if user_role == 1:
#         # Collector (Role 1) sees only their own data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).filter(collector=request.user)
#     else:
#         # Admin (Role 2) or others see all data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).all()

#     # Apply filters
#     if district_filter:
#         all_data = all_data.filter(localbody__district__id=district_filter)

#     if localbody_filter:
#         all_data = all_data.filter(localbody__id=localbody_filter)

#     if phone_filter:
#         all_data = all_data.filter(
#             Q(customer__contact_number__icontains=phone_filter) |
#             Q(collector__contact_number__icontains=phone_filter)
#         )

#     if from_date_filter:
#         try:
#             from_date = datetime.strptime(from_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__gte=from_date)
#         except ValueError:
#             pass

#     if to_date_filter:
#         try:
#             to_date = datetime.strptime(to_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__lte=to_date)
#         except ValueError:
#             pass

#     # Filter by month if requested (legacy functionality)
#     month_filter = request.GET.get('month')
#     if month_filter == 'current':
#         from django.utils import timezone
#         now = timezone.now()
#         first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         all_data = all_data.filter(created_at__gte=first_day_of_month)

#     # Order by created_at descending
#     all_data = all_data.order_by('-created_at')

#     # Get districts and localbodies for filter dropdowns
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Final districts count: {districts.count()}")
#     print(f"DEBUG: Final localbodies count: {localbodies.count()}")
#     print(f"DEBUG: Filtered data count: {all_data.count()}")

#     # Handle AJAX request for filtered data
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         # Prepare data for JSON response
#         data = []
#         for item in all_data:
#             data.append({
#                 'id': item.id,
#                 'collector': item.collector.username,
#                 'customer': item.customer.username,
#                 'localbody': item.localbody.name if item.localbody else 'Not assigned',
#                 'ward': item.ward,
#                 'location': item.location,
#                 'number_of_bags': item.number_of_bags,
#                 'building_no': item.building_no,
#                 'street_name': item.street_name,
#                 'kg': float(item.kg),
#                 'total_amount': float(item.total_amount) if item.total_amount else 0,
#                 'payment_method': item.get_payment_method_display(),
#                 'photo_url': item.photo.url if item.photo else None,
#                 'booking_date': item.booking_date.strftime('%Y-%m-%d %H:%M') if item.booking_date else '',
#                 'collection_time': item.collection_time.strftime('%H:%M') if item.collection_time else '',
#                 'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                 'scheduled_date': item.scheduled_date.strftime('%Y-%m-%d') if item.scheduled_date else '',
#             })

#         return JsonResponse({
#             'data': data,
#             'total_count': len(data)
#         })

#     return render(request, 'view_collected_data.html', {
#         'all_data': all_data,
#         'districts': districts,
#         'localbodies': localbodies,
#         'selected_district': district_filter,
#         'selected_localbody': localbody_filter,
#         'selected_phone': phone_filter,
#         'selected_from_date': from_date_filter,
#         'selected_to_date': to_date_filter,
#         'all_data': all_data
#     })


# # ////// MAP_ROLE
# @login_required
# def map_role(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         new_role = request.POST.get("role")
#         if new_role is not None:
#             try:
#                 new_role = int(new_role)  # Convert string to int
#                 if new_role in dict(CustomUser.ROLE_CHOICES).keys():
#                     user.role = new_role
#                     user.save()
#                     return redirect("super_admin_dashboard:users_list")
#             except ValueError:
#                 pass  # Ignore invalid input
#     return render(request, "map_role.html", {"user": user, "roles": CustomUser.ROLE_CHOICES})







# # ////////////////////////////      CALENDAR SET UP     ///////////////////////////////////


# import json
# from datetime import date, datetime, timedelta

# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
# from django.views.decorators.http import require_POST, require_GET
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.utils.dateparse import parse_date
# from django.template.loader import get_template


# from .models import State, District, LocalBody, LocalBodyCalendar
# from .utils import is_super_admin





# @login_required
# @user_passes_test(is_super_admin)
# def calendar_view(request):
#     """Main page where admin picks state/district/localbody and sees FullCalendar."""
#     states = State.objects.all().order_by("name")
#     return render(request, "calendar.html", {"states": states})


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_districts(request, state_id):
#     districts = District.objects.filter(state_id=state_id).values("id", "name")
#     return JsonResponse(list(districts), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_localbodies(request, district_id):
#     lbs = LocalBody.objects.filter(district_id=district_id).values("id", "name", "body_type")
#     return JsonResponse(list(lbs), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_wards(request, localbody_id):
#     """Load wards for a specific localbody"""
#     try:
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         # Convert to the format expected by the frontend
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# # Test endpoint without authentication for debugging
# def debug_wards_no_auth(request, localbody_id):
#     """Debug endpoint to test ward loading without authentication"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         print(f"DEBUG NO AUTH: Loading wards for localbody_id {localbody_id}")
#         print(f"DEBUG NO AUTH: Found {len(wards_data)} wards")
#         print(f"DEBUG NO AUTH: Sample data: {wards_data[:2] if wards_data else 'None'}")
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         print(f"DEBUG NO AUTH: Error: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates(request, localbody_id):
#     events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#     # FullCalendar expects events with at least id and start
#     data = [{"id": e["id"], "title": "Assigned", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates_by_ward(request, localbody_id):
#     """Get calendar dates filtered by ward number"""
#     ward_number = request.GET.get('ward')
#     if ward_number:
#         # For now, we'll return all calendar dates for the localbody
#         # In a more advanced implementation, you might have ward-specific calendar entries
#         events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#         data = [{"id": e["id"], "title": f"Assigned - Ward {ward_number}", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     else:
#         data = []
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def create_calendar_date(request, localbody_id):
#     """Create one date or range. Expects 'date' in YYYY-MM-DD or 'start' & 'end' for ranges."""
#     lb = get_object_or_404(LocalBody, pk=localbody_id)

#     # support single-date or start/end
#     start = request.POST.get("start")
#     end = request.POST.get("end")
#     single = request.POST.get("date")

#     created = []
#     if single:
#         d = parse_date(single)
#         if not d:
#             return HttpResponseBadRequest("Invalid date")
#         entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=d)
#         if created_flag:
#             created.append({"id": entry.id, "date": entry.date.isoformat()})
#         return JsonResponse({"status": "created", "created": created})

#     if start and end:
#         s = parse_date(start)
#         e = parse_date(end)
#         if not s or not e:
#             return HttpResponseBadRequest("Invalid start/end")
#         cur = s
#         while cur <= e:
#             entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=cur)
#             if created_flag:
#                 created.append({"id": entry.id, "date": entry.date.isoformat()})
#             cur += timedelta(days=1)
#         return JsonResponse({"status": "created_range", "created": created})

#     return HttpResponseBadRequest("Provide 'date' or 'start' and 'end'.")


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def update_calendar_date(request, pk):
#     """Change date for an existing LocalBodyCalendar entry. Expect 'new_date' YYYY-MM-DD"""
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     new_date_raw = request.POST.get("new_date")
#     if not new_date_raw:
#         return HttpResponseBadRequest("Missing new_date")
#     new_date = parse_date(new_date_raw.split("T")[0])
#     if not new_date:
#         return HttpResponseBadRequest("Invalid date")
#     # prevent duplicates: if another entry exists for that localbody on same date -> reject
#     exists = LocalBodyCalendar.objects.filter(localbody=entry.localbody, date=new_date).exclude(pk=entry.pk).exists()
#     if exists:
#         return JsonResponse({"status": "conflict", "message": "Date already assigned"}, status=409)
#     entry.date = new_date
#     entry.save()
#     return JsonResponse({"status": "updated", "id": entry.id, "date": entry.date.isoformat()})


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def delete_calendar_date(request, pk):
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     entry.delete()
#     return JsonResponse({"status": "deleted", "id": pk})






# # /////////////// super admin create waste oder


# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser
# from super_admin_dashboard.models import State, District, LocalBody
# @login_required
# def create_waste_profile(request):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     if request.method == "POST":
#         contact_number = request.POST.get("contact_number")

#         # Step 1: Check if customer exists
#         try:
#             customer = CustomUser.objects.get(contact_number=contact_number, role=0)
#         except CustomUser.DoesNotExist:
#             messages.error(request, "No registered customer found with this contact number.")
#             return redirect("super_admin_dashboard:create_waste_profile")

#         # Step 2: Collect waste info details from form
#         full_name = request.POST.get("full_name")
#         secondary_number = request.POST.get("secondary_number")
#         pickup_address = request.POST.get("pickup_address")
#         landmark = request.POST.get("landmark")
#         pincode = request.POST.get("pincode")
#         state_id = request.POST.get("state")
#         district_id = request.POST.get("district")
#         localbody_id = request.POST.get("localbody")
#         waste_type = request.POST.get("waste_type")
#         number_of_bags = request.POST.get("number_of_bags")
#         ward = request.POST.get("ward")
#         selected_date_id = request.POST.get("selected_date")  # calendar selected date

#         # Step 3: Create Waste Profile
#         waste_info = CustomerWasteInfo.objects.create(
#             user=customer,
#             full_name=full_name,
#             secondary_number=secondary_number,
#             pickup_address=pickup_address,
#             landmark=landmark,
#             pincode=pincode,
#             state_id=state_id,
#             district_id=district_id,
#             localbody_id=localbody_id,
#             waste_type=waste_type,
#             number_of_bags=number_of_bags,
#             ward=ward
#         )

#         # Step 4: Save pickup date if given
#         if selected_date_id:
#             try:
#                 cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                 CustomerPickupDate.objects.create(
#                     user=customer,
#                     waste_info=waste_info,
#                     localbody_calendar=cal
#                 )
#             except LocalBodyCalendar.DoesNotExist:
#                 messages.warning(request, "Invalid pickup date selected.")

#         messages.success(request, f"Waste profile created for {customer.first_name}")
#         return redirect("super_admin_dashboard:view_customer_waste_info")

#     # GET request
#     states = State.objects.all()
#     ward_range = range(1, 74)  # Wards 1–73
#     bag_range = range(1, 11)   # Bags 1–10
#     # For super admin form, we don't have a localbody selected yet, so show numbers only
#     ward_options = get_ward_options(None)

#     return render(request, "superadmin_waste_form.html", {
#         "states": states,
#         "ward_range": ward_range,
#         "bag_range": bag_range,
#         "ward_options": ward_options,
#     })




# from .forms import WasteProfileForm  # we'll create this form



# @login_required
# def view_waste_profile(request, pk):
#     waste_info = get_object_or_404(
#         CustomerWasteInfo.objects.select_related(
#             "user", "state", "district", "localbody", "assigned_collector"
#         ),
#         pk=pk
#     )

#     # pickup dates for this profile
#     pickup_dates = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     return render(request, "superadmin_view_waste.html", {
#         "info": waste_info,
#         "pickup_dates": pickup_dates,
#     })



# @login_required
# def edit_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     existing_pickups = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     if request.method == "POST":
#         form = WasteProfileForm(request.POST, instance=waste_info)
#         if form.is_valid():
#             waste_info = form.save()

#             selected_date_id = request.POST.get("selected_date")
#             if selected_date_id:
#                 try:
#                     cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                     CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={"localbody_calendar": cal}
#                     )
#                 except LocalBodyCalendar.DoesNotExist:
#                     messages.warning(request, "⚠️ Invalid pickup date selected.")

#             messages.success(request, "✅ Waste profile updated successfully.")
#             return redirect("super_admin_dashboard:waste_info_list")
#     else:
#         form = WasteProfileForm(instance=waste_info)

#     available_dates = LocalBodyCalendar.objects.filter(localbody=waste_info.localbody).order_by("date")
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {districts.count()}")
#     print(f"DEBUG: LocalBodies count: {localbodies.count()}")
#     print(f"DEBUG: Selected filters - District: {request.GET.get('district_filter')}, LocalBody: {request.GET.get('localbody_filter')}, Phone: {request.GET.get('phone_filter')}")

#     return render(request, "superadmin_edit_waste.html", {
#         "form": form,
#         "info": waste_info,
#         "existing_pickups": existing_pickups,
#         "available_dates": available_dates,
#         "districts": districts,
#         "localbodies": localbodies
#     })



# @login_required
# def delete_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     if request.method == "POST":
#         waste_info.delete()
#         messages.success(request, "🗑️ Waste profile deleted successfully.")
#         return redirect("super_admin_dashboard:waste_info_list")  # ✅ updated

#     return render(request, "superadmin_confirm_delete.html", {
#         "info": waste_info
#     })


# from django.core.paginator import Paginator
# from django.db.models import Q

# @login_required
# def waste_info_list(request):
#     search_query = request.GET.get("q", "")   # search input
#     page_number = request.GET.get("page", 1)  # current page

#     # Fetch all customer waste profiles
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         "state", "district", "localbody", "assigned_collector", "user"
#     ).prefetch_related("customerpickupdate_set__localbody_calendar")

#     # ✅ Search filter (name / phone / address)
#     if search_query:
#         waste_infos = waste_infos.filter(
#             Q(user__first_name__icontains=search_query) |
#             Q(user__last_name__icontains=search_query) |
#             Q(user__contact_number__icontains=search_query) |
#             Q(pickup_address__icontains=search_query)
#         )

#     # ✅ Pagination (10 profiles per page)
#     paginator = Paginator(waste_infos.order_by("-id"), 10)
#     page_obj = paginator.get_page(page_number)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     return render(request, "waste_info_list.html", {
#         "page_obj": page_obj,
#         "collectors": collectors,
#         "search_query": search_query,
#     })

# @login_required
# @user_passes_test(is_super_admin)
# def load_localbodies_for_reports(request):
#     district_id = request.GET.get('district_id')
#     localbodies = LocalBody.objects.filter(district_id=district_id).values("id", "name") if district_id else []
#     return JsonResponse(list(localbodies), safe=False)

# @login_required
# @user_passes_test(is_super_admin)
# def generate_reports(request):
#     """
#     View to display the reports page.
#     """
#     return render(request, 'reports.html')

# @login_required
# @user_passes_test(is_super_admin)
# def generate_report(request):
#     """Generate various types of reports"""
#     if request.method == 'POST':
#         try:
#             report_type = request.POST.get('report_type')
#             print(f"Generating report type: {report_type}")

#             # Get real data for reports
#             from customer_dashboard.models import CustomerWasteInfo
#             from authentication.models import CustomUser
#             from waste_collector_dashboard.models import WasteCollection
#             from datetime import date, datetime, timedelta

#             # Initialize report data
#             report_data = {
#                 'report_type': report_type,
#                 'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                 'report_name': f"{report_type.replace('_', ' ').title()} Report"
#             }

#             # Generate specific report data based on type
#             if report_type == 'daily_collection':
#                 # Get today's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date=today
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'collections_data': [{
#                         'customer': col.customer.get_full_name() if col.customer else 'Unknown',
#                         'address': col.location,
#                         'waste_type': col.customer.customerwasteinfo_set.first().waste_type if col.customer and col.customer.customerwasteinfo_set.exists() else 'Unknown',
#                         'bags': col.number_of_bags,
#                         'collected_at': col.collection_time.strftime('%H:%M') if col.collection_time else 'N/A'
#                     } for col in collections]
#                 })

#             elif report_type == 'weekly_collection':
#                 # Get this week's collections
#                 today = date.today()
#                 week_start = today - timedelta(days=today.weekday())
#                 week_end = week_start + timedelta(days=6)

#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__range=[week_start, week_end]
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
#                 })

#             elif report_type == 'monthly_collection':
#                 # Get this month's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__year=today.year,
#                     scheduled_date__month=today.month
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': today.strftime('%B %Y')
#                 })

#             elif report_type == 'customer_summary':
#                 # Get customer summary data
#                 customers = CustomUser.objects.filter(role=0)
#                 total_customers = customers.count()
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).count()

#                 report_data.update({
#                     'total_customers': total_customers,
#                     'active_customers': active_customers,
#                     'new_customers_this_month': active_customers
#                 })

#             elif report_type == 'active_customers':
#                 # Get active customers
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).select_related('user', 'state', 'district', 'localbody')

#                 report_data.update({
#                     'total_active_customers': active_customers.count(),
#                     'customer_list': [{
#                         'name': info.user.get_full_name() if info.user else 'Unknown',
#                         'phone': info.user.contact_number if hasattr(info.user, 'contact_number') else 'N/A',
#                         'address': info.pickup_address if hasattr(info, 'pickup_address') else 'N/A',
#                         'waste_type': info.waste_type,
#                         'status': info.status,
#                         'last_collection': 'N/A',
#                         'days_since_last': 'N/A'
#                     } for info in active_customers]
#                 })

#             elif report_type == 'payment_analysis':
#                 report_data.update({
#                     'payment_analysis': 'Payment analysis data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'outstanding_payments':
#                 report_data.update({
#                     'outstanding_payments': 'Outstanding payments data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'collector_performance':
#                 # Analyze collector performance
#                 collectors = CustomUser.objects.filter(role=1)
#                 performance_data = []

#                 for collector in collectors:
#                     try:
#                         # Get collections for this collector this month
#                         collector_collections = WasteCollection.objects.filter(
#                             collector=collector,
#                             scheduled_date__month=date.today().month,
#                             scheduled_date__year=date.today().year
#                         )

#                         total_collections = collector_collections.count()
#                         total_bags = sum(col.number_of_bags for col in collector_collections)

#                         performance_data.append({
#                             'collector_name': collector.get_full_name(),
#                             'total_collections': total_collections,
#                             'total_bags': total_bags,
#                             'days_worked': len(set(col.scheduled_date for col in collector_collections if col.scheduled_date)),
#                         })
#                     except Exception as e:
#                         print(f"Error processing collector {collector.id}: {e}")
#                         continue

#                 # Sort by performance
#                 performance_data.sort(key=lambda x: x['total_collections'], reverse=True)

#                 report_data.update({
#                     'period': date.today().strftime('%B %Y'),
#                     'total_collectors': len(collectors),
#                     'performance_data': performance_data,
#                     'top_performers': performance_data[:5]
#                 })

#             elif report_type == 'efficiency_metrics':
#                 report_data.update({
#                     'efficiency_metrics': 'Operational efficiency metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'service_level':
#                 report_data.update({
#                     'service_level': 'Service level metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             else:
#                 return JsonResponse({'success': False, 'error': f'Unknown report type: {report_type}'}, status=400)

#             print("Report generated successfully:", report_data)
#             return JsonResponse({
#                 'success': True,
#                 'report_data': report_data,
#                 'report_name': report_data['report_name']
#             })

#         except Exception as e:
#             error_msg = str(e)
#             print("Error generating report:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# @login_required
# @user_passes_test(is_super_admin)
# def load_districts_for_reports(request):
#     state_id = request.GET.get('state_id')
#     districts = District.objects.filter(state_id=state_id).values("id", "name") if state_id else []
#     return JsonResponse(list(districts), safe=False)


#   # Get additional data for CRUD functionality
#     from authentication.models import CustomUser
#     from super_admin_dashboard.models import LocalBody

#     all_customers = CustomUser.objects.filter(role=0)  # Customers
#     all_localbodies = LocalBody.objects.all()

#     try:
#         response = render(request, 'view_collected_data.html', {
#             'all_data': all_data,
#             'all_customers': all_customers,
#             'all_localbodies': all_localbodies,
#         })
#         print("Template rendered successfully")
#         print("=======================================")
#         return response
#     except Exception as e:
#         print(f"ERROR rendering template: {e}")
#         import traceback
#         traceback.print_exc()
#         raise


# # CRUD Operations for Waste Collection
# @login_required
# @user_passes_test(can_view_collected_data)
# def update_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)

#         # Update fields based on POST data
#         waste_collection.ward = request.POST.get('ward', waste_collection.ward)
#         waste_collection.location = request.POST.get('location', waste_collection.location)
#         waste_collection.number_of_bags = request.POST.get('number_of_bags', waste_collection.number_of_bags)
#         waste_collection.building_no = request.POST.get('building_no', waste_collection.building_no)
#         waste_collection.street_name = request.POST.get('street_name', waste_collection.street_name)
#         waste_collection.kg = request.POST.get('kg', waste_collection.kg)

#         # Handle customer and localbody foreign keys
#         if request.POST.get('customer'):
#             customer_id = int(request.POST.get('customer'))
#             waste_collection.customer = CustomUser.objects.get(id=customer_id, role=0)

#         if request.POST.get('localbody'):
#             localbody_id = int(request.POST.get('localbody'))
#             waste_collection.localbody = LocalBody.objects.get(id=localbody_id)

#         # Handle date fields
#         scheduled_date_str = request.POST.get('scheduled_date')
#         if scheduled_date_str:
#             waste_collection.scheduled_date = scheduled_date_str
#         elif scheduled_date_str == '':
#             waste_collection.scheduled_date = None

#         # Handle time field
#         collection_time_str = request.POST.get('collection_time')
#         if collection_time_str:
#             from datetime import datetime
#             time_obj = datetime.strptime(collection_time_str, '%H:%M').time()
#             waste_collection.collection_time = time_obj
#         elif collection_time_str == '':
#             waste_collection.collection_time = None

#         # Recalculate total amount if kg or rate changes
#         waste_collection.save()

#         return JsonResponse({'success': True, 'message': 'Record updated successfully'})

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected customer does not exist'})
#     except LocalBody.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected local body does not exist'})
#     except ValueError as e:
#         return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})


# @login_required
# @user_passes_test(can_view_collected_data)
# def delete_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)
#         waste_collection.delete()
#         return JsonResponse({'success': True, 'message': 'Record deleted successfully'})

#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})







# @login_required
# @user_passes_test(is_super_admin)
# def export_all_users_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"all_users_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Role', 'Contact Number', 'Date Joined'])

#     users = CustomUser.objects.all().order_by('id')

#     for user in users:
#         writer.writerow([
#             user.id,
#             user.username,
#             user.first_name,
#             user.last_name,
#             user.email,
#             user.get_role_display(),
#             user.contact_number,
#             user.date_joined.strftime("%Y-%m-%d %H:%M") if user.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_customers_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"customers_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     customers = CustomUser.objects.filter(role=0)

#     for customer in customers:
#         writer.writerow([
#             customer.id,
#             customer.username,
#             customer.first_name,
#             customer.last_name,
#             customer.email,
#             customer.contact_number,
#             customer.date_joined.strftime("%Y-%m-%d %H:%M") if customer.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_collectors_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"collectors_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     collectors = CustomUser.objects.filter(role=1)

#     for collector in collectors:
#         writer.writerow([
#             collector.id,
#             collector.username,
#             collector.first_name,
#             collector.last_name,
#             collector.email,
#             collector.contact_number,
#             collector.date_joined.strftime("%Y-%m-%d %H:%M") if collector.date_joined else 'N/A'
#         ])

#     return response


# # Test endpoint for debugging with authentication
# @login_required
# @user_passes_test(is_super_admin)
# def test_wards_endpoint(request, localbody_id):
#     """Test endpoint to verify ward loading is working"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse({
#             "status": "success",
#             "localbody_id": localbody_id,
#             "localbody_name": localbody.name,
#             "ward_count": len(data),
#             "wards": data
#         })
#     except LocalBody.DoesNotExist:
#         return JsonResponse({
#             "status": "error",
#             "message": "Local body not found"
#         }, status=404)
#     except Exception as e:
#         return JsonResponse({
#             "status": "error",
#             "message": str(e)
#         }, status=500)


# # Price Control Views
# @login_required
# @user_passes_test(is_super_admin)
# def price_control(request):
#     """Price control page for managing waste collection pricing"""
#     from .models import District, LocalBody, WasteTypePrice, ServiceFee, LocationPriceMultiplier

#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Get existing pricing data
#     waste_prices = WasteTypePrice.objects.all()
#     service_fee = ServiceFee.objects.first()
#     location_multipliers = LocationPriceMultiplier.objects.select_related('district', 'localbody').all()

#     context = {
#         'districts': districts,
#         'localbodies': localbodies,
#         'waste_prices': waste_prices,
#         'service_fee': service_fee,
#         'location_multipliers': location_multipliers,
#     }
#     return render(request, 'price_control.html', context)


# @login_required
# @user_passes_test(is_super_admin)
# def load_price_history(request):
#     """Load price history for display"""
#     if request.method == 'GET':
#         try:
#             from .models import PriceHistory
#             from django.core.serializers.json import DjangoJSONEncoder

#             history = PriceHistory.objects.select_related('updated_by').order_by('-created_at')[:20]

#             history_data = []
#             for item in history:
#                 history_data.append({
#                     'date': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                     'type': item.pricing_type.replace('_', ' ').title(),
#                     'category': item.category,
#                     'old_price': f"₹{item.old_value}" if item.old_value else '-',
#                     'new_price': f"₹{item.new_value}" if item.new_value else '-',
#                     'updated_by': item.updated_by.get_full_name() if item.updated_by else 'System',
#                     'status': 'active' if item.action_type == 'create' else 'updated'
#                 })

#             return JsonResponse({
#                 'success': True,
#                 'data': history_data
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_waste_price(request):
#     """Save waste type pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import WasteTypePrice, PriceHistory
#             data = json.loads(request.body)

#             waste_type = data.get('waste_type')
#             price_per_kg = data.get('price_per_kg')
#             status = data.get('status', 'active')

#             # Validate input
#             if not waste_type or price_per_kg is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             price_per_kg = float(price_per_kg)
#             if price_per_kg < 0:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price must be non-negative'
#                 })

#             # Get or create waste type price
#             waste_price, created = WasteTypePrice.objects.get_or_create(
#                 waste_type=waste_type,
#                 defaults={
#                     'price_per_kg': price_per_kg,
#                     'status': status,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_price = waste_price.price_per_kg
#                 waste_price.price_per_kg = price_per_kg
#                 waste_price.status = status
#                 waste_price.updated_by = request.user
#                 waste_price.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     old_value=old_price,
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Waste type price saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_service_fees(request):
#     """Save service fee pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import ServiceFee, PriceHistory
#             data = json.loads(request.body)

#             base_fee = data.get('base_fee')
#             fee_per_bag = data.get('fee_per_bag')
#             min_charge = data.get('min_charge')

#             # Validate input
#             if base_fee is None or fee_per_bag is None or min_charge is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             base_fee = float(base_fee)
#             fee_per_bag = float(fee_per_bag)
#             min_charge = float(min_charge)

#             if any(x < 0 for x in [base_fee, fee_per_bag, min_charge]):
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'All fees must be non-negative'
#                 })

#             # Get or create service fee
#             service_fee, created = ServiceFee.objects.get_or_create(
#                 pk=1,  # Assume single service fee record
#                 defaults={
#                     'base_fee': base_fee,
#                     'fee_per_bag': fee_per_bag,
#                     'min_charge': min_charge,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_base_fee = service_fee.base_fee
#                 old_fee_per_bag = service_fee.fee_per_bag
#                 old_min_charge = service_fee.min_charge

#                 service_fee.base_fee = base_fee
#                 service_fee.fee_per_bag = fee_per_bag
#                 service_fee.min_charge = min_charge
#                 service_fee.updated_by = request.user
#                 service_fee.save()

#                 # Log changes to history
#                 if old_base_fee != base_fee:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Base Fee',
#                         old_value=old_base_fee,
#                         new_value=base_fee,
#                         updated_by=request.user
#                     )

#                 if old_fee_per_bag != fee_per_bag:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Fee per Bag',
#                         old_value=old_fee_per_bag,
#                         new_value=fee_per_bag,
#                         updated_by=request.user
#                     )

#                 if old_min_charge != min_charge:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Minimum Charge',
#                         old_value=old_min_charge,
#                         new_value=min_charge,
#                         updated_by=request.user
#                     )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='service_fee',
#                     category='Service Fees',
#                     new_value=base_fee,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Service fees saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_location_multiplier(request):
#     """Save location-based price multiplier"""
#     if request.method == 'POST':
#         try:
#             from .models import LocationPriceMultiplier, PriceHistory, District, LocalBody
#             data = json.loads(request.body)

#             # Validate price multiplier
#             price_multiplier = float(data.get('price_multiplier', 0))
#             if price_multiplier > 500.0 or price_multiplier < 0.1:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price multiplier must be between 0.1 and 500.0'
#                 })

#             district_id = data.get('district')
#             localbody_id = data.get('localbody')

#             if not district_id or not localbody_id:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'District and Local Body are required'
#                 })

#             # Get district and localbody objects
#             district = District.objects.get(id=district_id)
#             localbody = LocalBody.objects.get(id=localbody_id)

#             # Get or create location price multiplier
#             location_multiplier, created = LocationPriceMultiplier.objects.get_or_create(
#                 district=district,
#                 localbody=localbody,
#                 defaults={
#                     'price_multiplier': price_multiplier,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_multiplier = location_multiplier.price_multiplier
#                 location_multiplier.price_multiplier = price_multiplier
#                 location_multiplier.updated_by = request.user
#                 location_multiplier.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     old_value=old_multiplier,
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Location multiplier saved successfully'
#             })
#         except ValueError:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid price multiplier value'
#             })
#         except District.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'District not found'
#             })
#         except LocalBody.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Local Body not found'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


























# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render, redirect,get_object_or_404
# from django.http import JsonResponse
# from authentication.models import CustomUser
# from waste_collector_dashboard.models import WasteCollection
# # from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate  # Moved inside functions to avoid circular import
# from django.contrib import messages
# from .utils import is_super_admin
# from django.template.loader import get_template, render_to_string
# from django.utils import timezone
# from django.db.models import Sum
# from datetime import datetime
# from .models import State, District, LocalBody, LocalBodyCalendar, Ward

# def get_ward_names():
#     """Return a dictionary mapping ward numbers to ward names"""
#     return {
#         1: "Fort Kochi",
#         2: "Kalvathy",
#         3: "Earavely",
#         4: "Karippalam",
#         5: "Cheralayi",
#         6: "Mattanchery",
#         7: "Chakkamadam",
#         8: "Karuvelippady",
#         9: "Island North",
#         10: "Ravipuram",
#         11: "Ernakulam South",
#         12: "Gandhi Nagar",
#         13: "Kathrikadavu",
#         14: "Ernakulam Central",
#         15: "Ernakulam North",
#         16: "Kaloor South",
#         17: "Kaloor North",
#         18: "Thrikkanarvattom",
#         19: "Ayyappankavu",
#         20: "Pottakuzhy",
#         21: "Elamakkara South",
#         22: "Pachalam",
#         23: "Thattazham",
#         24: "Vaduthala West",
#         25: "Vaduthala East",
#         26: "Elamakkara North",
#         27: "Puthukkalavattam",
#         28: "Kunnumpuram",
#         29: "Ponekkara",
#         30: "Edappally",
#         31: "Changampuzha",
#         32: "Dhevankulangara",
#         33: "Palarivattom",
#         34: "Stadium",
#         35: "Karanakkodam",
#         36: "Puthiyaroad",
#         37: "Padivattam",
#         38: "Vennala",
#         39: "Chakkaraparambu",
#         40: "Chalikkavattam",
#         41: "Thammanam",
#         42: "Elamkulam",
#         43: "Girinagar",
#         44: "Ponnurunni",
#         45: "Ponnurunni East",
#         46: "Vyttila",
#         47: "Poonithura",
#         48: "Vyttila Janatha",
#         49: "Kadavanthra",
#         50: "Panampilly Nagar",
#         51: "Perumanoor",
#         52: "Konthuruthy",
#         53: "Thevara",
#         54: "Island South",
#         55: "Kadebhagam",
#         56: "Palluruthy East",
#         57: "Thazhuppu",
#         58: "Eadakochi North",
#         59: "Edakochi South",
#         60: "Perumbadappu",
#         61: "Konam",
#         62: "Palluruthy Kacheripady",
#         63: "Nambyapuram",
#         64: "Palluruthy",
#         65: "Pullardesam",
#         66: "Tharebhagam",
#         67: "Thoppumpady",
#         68: "Mundamvely East",
#         69: "Mundamvely",
#         70: "Manassery",
#         71: "Moolamkuzhy",
#         72: "Chullickal",
#         73: "Nasrathu",
#         74: "Panayappilly",
#         75: "Amaravathy",
#         76: "Fortkochi Veli"
#     }

# def get_ward_options(localbody_name=None):
#     """Kochi/Ernakulam → 76 named wards (Fort Kochi, etc.); other local bodies → Ward 1 to Ward 10."""
#     ward_names = get_ward_names()
#     name_lower = (localbody_name or '').lower()
#     if name_lower and ('kochi' in name_lower or 'ernakulam' in name_lower):
#         return [(i, ward_names.get(i, f'Ward {i}')) for i in range(1, 77)]
#     return [(i, f'Ward {i}') for i in range(1, 11)]


# @login_required
# def admin_home(request):
#     from customer_dashboard.models import CustomerPickupDate, CustomerWasteInfo
#     from django.db.models import Count, Q

#     # Get current date info
#     now = timezone.now()
#     first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

#     # Calculate statistics
#     total_customers = CustomUser.objects.filter(role=0).count()
#     total_collectors = CustomUser.objects.filter(role=1).count()

#     # Collections this month
#     monthly_collections = WasteCollection.objects.filter(
#         created_at__gte=first_day_of_month
#     ).count()

#     # Total waste collected (sum of kg)
#     total_waste_collected_data = WasteCollection.objects.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     # 1. Collection Rate: Collections vs Scheduled Pickups
#     scheduled_pickups = CustomerPickupDate.objects.filter(
#         localbody_calendar__date__gte=first_day_of_month.date(),
#         localbody_calendar__date__lte=now.date()
#     ).count()

#     collection_rate = 0
#     if scheduled_pickups > 0:
#         collection_rate = min(100, int((monthly_collections / scheduled_pickups) * 100))
#     elif monthly_collections > 0:
#         collection_rate = 100

#     # 2. Customer Satisfaction: Based on "On-Time" collections
#     # If scheduled_date == collection_date or matches within 1 day
#     on_time_collections = 0
#     total_with_schedule = 0
#     collections_with_schedule = WasteCollection.objects.filter(
#         scheduled_date__isnull=False,
#         created_at__gte=first_day_of_month
#     )

#     for coll in collections_with_schedule:
#         total_with_schedule += 1
#         # Compare created_at date with scheduled_date
#         collection_date = coll.created_at.date()
#         scheduled_date = coll.scheduled_date

#         # Ensure we are comparing date to date (scheduled_date might be datetime in some cases)
#         if hasattr(scheduled_date, 'date'):
#             scheduled_date = scheduled_date.date()

#         if collection_date <= scheduled_date:
#             on_time_collections += 1

#     customer_satisfaction = 4.5 # Default high starting point
#     if total_with_schedule > 0:
#         satisfaction_ratio = on_time_collections / total_with_schedule
#         customer_satisfaction = round(3.0 + (satisfaction_ratio * 2.0), 1) # Scale between 3.0 and 5.0

#     # 3. Recycling Rate: Estimated based on waste types
#     # Check CustomerWasteInfo for recyclable types
#     recyclable_keywords = ['plastic', 'paper', 'metal', 'glass', 'can', 'bottle', 'recyclable']
#     recyclable_query = Q()
#     for kw in recyclable_keywords:
#         recyclable_query |= Q(waste_type__icontains=kw)

#     total_profiles = CustomerWasteInfo.objects.count()
#     recyclable_profiles = CustomerWasteInfo.objects.filter(recyclable_query).count()

#     recycling_rate = 0
#     if total_profiles > 0:
#         recycling_rate = int((recyclable_profiles / total_profiles) * 100)
#     else:
#         recycling_rate = 65 # Reasonable industry average placeholder if no data

#     # Get order data for control all orders functionality
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'user', 'state', 'district', 'localbody', 'assigned_collector'
#     ).all()

#     total_orders = waste_infos.count()
#     pending_orders = waste_infos.filter(status='pending').count()
#     confirmed_orders = waste_infos.filter(status='in_progress').count()
#     completed_orders = waste_infos.filter(status='completed').count()

#     # Get all collectors for dropdown
#     collectors = CustomUser.objects.filter(role=1)

#     # Build orders data from real CustomerWasteInfo
#     orders = []
#     for info in waste_infos[:20]:  # Limit to first 20 orders
#         try:
#             # Get scheduled date for this waste info
#             pickup_date = info.customerpickupdate_set.select_related('localbody_calendar').first()
#             scheduled_date_order = pickup_date.localbody_calendar.date.strftime('%Y-%m-%d') if pickup_date and pickup_date.localbody_calendar else 'Not Scheduled'

#             # Get assigned collector name
#             collector_name = info.assigned_collector.get_full_name() if info.assigned_collector else 'Unassigned'

#             # Convert status to readable format
#             status_map = {
#                 'pending': 'Pending',
#                 'in_progress': 'In Progress',
#                 'completed': 'Completed',
#                 'collected': 'Collected'
#             }
#             readable_status = status_map.get(info.status, info.status)

#             order = {
#                 'id': info.id,
#                 'customer_name': info.full_name,
#                 'customer_phone': info.user.contact_number,
#                 'address': info.pickup_address,
#                 'waste_type': info.waste_type,
#                 'bags': info.number_of_bags or 0,
#                 'booking_date': info.created_at.strftime('%Y-%m-%d'),
#                 'scheduled_date': scheduled_date_order,
#                 'status': readable_status,
#                 'assigned_collector': collector_name,
#                 'ward': info.ward,
#                 'localbody': info.localbody.name if info.localbody else 'Not Assigned'
#             }
#             orders.append(order)
#         except Exception as e:
#             print(f"Error processing order {info.id}: {e}")
#             continue

#     context = {
#         'total_customers': total_customers,
#         'total_collectors': total_collectors,
#         'monthly_collections': monthly_collections,
#         'total_waste_collected': f"{total_waste_collected_data:.1f} KG",
#         'collection_rate': collection_rate,
#         'customer_satisfaction': customer_satisfaction,
#         'recycling_rate': recycling_rate,
#         'orders': orders,
#         'total_orders': total_orders,
#         'pending_orders': pending_orders,
#         'confirmed_orders': confirmed_orders,
#         'completed_orders': completed_orders,
#         'collectors': collectors
#     }

#     return render(request, 'super_admin_dashboard.html', context)


# @login_required
# def manage_order(request, order_id):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     # Add logging for debugging
#     print(f"manage_order called with order_id: {order_id}, method: {request.method}")
#     print(f"User authenticated: {request.user.is_authenticated}")
#     print(f"User: {request.user}")

#     if request.method == 'POST':
#         try:
#             action = request.POST.get('action')
#             print(f"Action: {action}")

#             # Get the waste info object
#             waste_info = CustomerWasteInfo.objects.get(id=order_id)
#             print(f"Waste info found: {waste_info.id}")

#             # Handle order management actions
#             if action == 'assign_collector':
#                 collector_id = request.POST.get('collector_id')
#                 print(f"Assigning collector: {collector_id}")
#                 if collector_id:
#                     collector = CustomUser.objects.get(id=collector_id, role=1)  # role=1 for collectors
#                     waste_info.assigned_collector = collector
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} assigned to collector successfully')
#                     print("Collector assigned successfully")

#             elif action == 'update_status':
#                 new_status = request.POST.get('status')
#                 print(f"Updating status to: {new_status}")
#                 if new_status in ['pending', 'in_progress', 'completed', 'collected']:
#                     waste_info.status = new_status
#                     waste_info.save()
#                     messages.success(request, f'Order {order_id} status updated to {new_status}')
#                     print("Status updated successfully")

#             elif action == 'reschedule':
#                 new_date = request.POST.get('new_date')
#                 print(f"Rescheduling to: {new_date}")
#                 if new_date:
#                     # First get or create the calendar entry if it doesn't exist
#                     calendar_entry, created = LocalBodyCalendar.objects.get_or_create(
#                         localbody=waste_info.localbody,
#                         date=new_date
#                     )
#                     # Update the scheduled date by creating/updating the CustomerPickupDate
#                     pickup_date, created = CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={'localbody_calendar': calendar_entry}
#                     )
#                     messages.success(request, f'Order {order_id} rescheduled to {new_date}')
#                     print("Order rescheduled successfully")

#             response_data = {'success': True}
#             print("Returning success response:", response_data)
#             return JsonResponse(response_data)

#         except CustomerWasteInfo.DoesNotExist:
#             error_msg = f'Order {order_id} not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except CustomUser.DoesNotExist:
#             error_msg = 'Collector not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except LocalBodyCalendar.DoesNotExist:
#             error_msg = 'Schedule date not found'
#             print("Error:", error_msg)
#             return JsonResponse({'success': False, 'error': error_msg}, status=404)
#         except Exception as e:
#             error_msg = str(e)
#             print("Unexpected error:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     # If not POST method
#     error_msg = 'Invalid request method'
#     print("Error:", error_msg)
#     return JsonResponse({'success': False, 'error': error_msg}, status=405)


# @login_required
# def user_list_view(request):
#     customers = CustomUser.objects.filter(role=0)
#     collectors = CustomUser.objects.filter(role=1)
#     admins = CustomUser.objects.filter(role=2)

#     return render(request, 'user_list.html', {
#         'customers': customers,
#         'collectors': collectors,
#         'admins': admins,
#     })
# @login_required
# def view_customers(request):
#     customers = CustomUser.objects.filter(role=0)
#     return render(request, 'view_customers.html', {'customers': customers})

# @login_required
# def view_waste_collectors(request):
#     collectors = CustomUser.objects.filter(role=1)
#     total_collectors = collectors.count()
#     service_areas = CollectorServiceArea.objects.select_related(
#         'collector', 'district', 'localbody'
#     ).order_by('collector__username', 'district__name', 'localbody__name')

#     # Get data for dropdowns (same style as view_collected_data)
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')  # kept for fallback/template safety

#     # Local body dropdown URL (login-only endpoint; filtered by district)
#     try:
#         load_localbodies_url = request.build_absolute_uri(
#             reverse('adminpanel:load_localbodies_collectors', args=[0])
#         ).replace('/0/', '/')
#     except Exception:
#         load_localbodies_url = request.build_absolute_uri('/admin/users/collectors/load-localbodies/')

#     # Ward dropdown URL (login-only endpoint for collectors page)
#     from django.urls import reverse
#     try:
#         load_wards_url = request.build_absolute_uri(
#             reverse('adminpanel:load_wards_collectors', args=[0])
#         ).replace('/0/', '/')
#     except Exception:
#         load_wards_url = request.build_absolute_uri('/admin/users/collectors/load-wards/')

#     return render(request, 'view_collectors.html', {
#         'collectors': collectors,
#         'total_collectors': total_collectors,
#         'service_areas': service_areas,
#         'districts': districts,
#         'localbodies': localbodies,
#         'load_localbodies_url': load_localbodies_url,
#         'load_wards_url': load_wards_url,
#     })
# @login_required
# def view_super_admin(request):
#     super_admin = CustomUser.objects.filter(role=2)
#     return render(request, "view_super_admin.html", {"super_admin":super_admin})

# @login_required
# def view_admins(request):
#     admins = CustomUser.objects.filter(role=3)
#     return render(request, "view_admins.html", {"admins":admins})

# # \\\\\\\\\\\\\\\\\\\\\\\\\\\ user view //////////////////////

# from .forms import UserForm

# @login_required
# def user_list(request):
#     users = CustomUser.objects.all()
#     return render(request, "users_list.html", {"users": users})





# @login_required
# def user_create(request):
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Encrypt password before saving
#                 user.set_password(password)
#             else:  # Default password if none provided
#                 user.set_password("default123")
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm()
#     return render(request, 'user_form.html', {'form': form})

# # Update User
# @login_required
# def user_update(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == 'POST':
#         form = UserForm(request.POST, instance=user)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Reset password if admin entered new one
#                 user.set_password(password)
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm(instance=user)
#     return render(request, 'user_form.html', {'form': form, 'user': user})






# # Delete user
# @login_required
# def user_delete(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         user.delete()
#         messages.success(request, "User deleted successfully")
#         return redirect("super_admin_dashboard:users_list")
#     return render(request, "user_confirm_delete.html", {"user": user})



# from django.shortcuts import render
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser

# @login_required
# def view_customer_wasteinfo(request):
#     # Fetch only unassigned customer waste profiles with related fields
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'state', 'district', 'localbody', 'assigned_collector', 'user'
#     ).filter(assigned_collector__isnull=True)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     # Map waste_info_id → pickup date
#     pickup_dates = {}
#     pickups = CustomerPickupDate.objects.select_related('localbody_calendar', 'waste_info').all()
#     for pickup in pickups:
#         if pickup.waste_info:
#             pickup_dates[pickup.waste_info.id] = pickup.localbody_calendar.date

#     return render(request, 'view_customer_wasteinfo.html', {
#         'waste_infos': waste_infos,
#         'collectors': collectors,
#         'pickup_dates': pickup_dates,
#     })

# # Assign a waste collector to a CustomerWasteInfo entry
# @login_required
# def assign_waste_collector(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)
#     if request.method == 'POST':
#         collector_id = request.POST.get('collector')
#         collector = get_object_or_404(CustomUser, pk=collector_id, role=1)

#         # Store customer info for success message
#         customer_name = waste_info.user.username
#         customer_address = waste_info.pickup_address

#         # Assign collector and ensure is_collected is False so it appears in assigned customers list
#         waste_info.assigned_collector = collector
#         waste_info.is_collected = False  # Mark as not collected so collector can see it
#         waste_info.save()

#         messages.success(request, f"Customer {customer_name} at {customer_address} has been assigned to {collector.username}. The customer now appears in the collector's assigned customers list.")
#         return redirect('super_admin_dashboard:view_customer_waste_info')

#     collectors = CustomUser.objects.filter(role=1)
#     return render(request, 'assign_waste_collector.html', {
#         'waste_info': waste_info,
#         'collectors': collectors,
#     })


# #waste collector collect details from customer

# def can_view_collected_data(user):
#     # Role 1 is Collector, Role 2 is Super Admin
#     return user.is_authenticated and (getattr(user, 'role', None) in [1, 2] or user.is_superuser)

# @login_required
# @user_passes_test(can_view_collected_data)
# def view_collected_data(request):
#     # Get waste collection data with related information
#     user_role = getattr(request.user, 'role', None)
#     try:
#         user_role = int(user_role)
#     except (TypeError, ValueError):
#         user_role = None

#     # Get filter parameters
#     district_filter = request.GET.get('district')
#     localbody_filter = request.GET.get('localbody')
#     phone_filter = request.GET.get('phone')
#     from_date_filter = request.GET.get('from_date')
#     to_date_filter = request.GET.get('to_date')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {District.objects.count()}")
#     print(f"DEBUG: LocalBodies count: {LocalBody.objects.count()}")
#     print(f"DEBUG: Selected filters - District: {district_filter}, LocalBody: {localbody_filter}, Phone: {phone_filter}")

#     # Base queryset
#     if user_role == 1:
#         # Collector (Role 1) sees only their own data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).filter(collector=request.user)
#     else:
#         # Admin (Role 2) or others see all data
#         all_data = WasteCollection.objects.select_related(
#             'collector', 'customer', 'localbody'
#         ).all()

#     # Apply filters
#     if district_filter:
#         all_data = all_data.filter(localbody__district__id=district_filter)

#     if localbody_filter:
#         all_data = all_data.filter(localbody__id=localbody_filter)

#     if phone_filter:
#         all_data = all_data.filter(
#             Q(customer__contact_number__icontains=phone_filter) |
#             Q(collector__contact_number__icontains=phone_filter)
#         )

#     if from_date_filter:
#         try:
#             from_date = datetime.strptime(from_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__gte=from_date)
#         except ValueError:
#             pass

#     if to_date_filter:
#         try:
#             to_date = datetime.strptime(to_date_filter, '%Y-%m-%d').date()
#             all_data = all_data.filter(created_at__date__lte=to_date)
#         except ValueError:
#             pass

#     # Filter by month if requested (legacy functionality)
#     month_filter = request.GET.get('month')
#     if month_filter == 'current':
#         from django.utils import timezone
#         now = timezone.now()
#         first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         all_data = all_data.filter(created_at__gte=first_day_of_month)

#     # Order by created_at descending
#     all_data = all_data.order_by('-created_at')

#     # Get districts and localbodies for filter dropdowns
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Final districts count: {districts.count()}")
#     print(f"DEBUG: Final localbodies count: {localbodies.count()}")
#     print(f"DEBUG: Filtered data count: {all_data.count()}")

#     # Handle AJAX request for filtered data
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         # Prepare data for JSON response
#         data = []
#         for item in all_data:
#             data.append({
#                 'id': item.id,
#                 'collector': item.collector.username,
#                 'customer': item.customer.username,
#                 'localbody': item.localbody.name if item.localbody else 'Not assigned',
#                 'ward': item.ward,
#                 'location': item.location,
#                 'number_of_bags': item.number_of_bags,
#                 'building_no': item.building_no,
#                 'street_name': item.street_name,
#                 'kg': float(item.kg),
#                 'total_amount': float(item.total_amount) if item.total_amount else 0,
#                 'payment_method': item.get_payment_method_display(),
#                 'photo_url': item.photo.url if item.photo else None,
#                 'booking_date': item.booking_date.strftime('%Y-%m-%d %H:%M') if item.booking_date else '',
#                 'collection_time': item.collection_time.strftime('%H:%M') if item.collection_time else '',
#                 'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                 'scheduled_date': item.scheduled_date.strftime('%Y-%m-%d') if item.scheduled_date else '',
#             })

#         return JsonResponse({
#             'data': data,
#             'total_count': len(data)
#         })

#     return render(request, 'view_collected_data.html', {
#         'all_data': all_data,
#         'districts': districts,
#         'localbodies': localbodies,
#         'selected_district': district_filter,
#         'selected_localbody': localbody_filter,
#         'selected_phone': phone_filter,
#         'selected_from_date': from_date_filter,
#         'selected_to_date': to_date_filter,
#         'all_data': all_data
#     })


# # ////// MAP_ROLE
# @login_required
# def map_role(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         new_role = request.POST.get("role")
#         if new_role is not None:
#             try:
#                 new_role = int(new_role)  # Convert string to int
#                 if new_role in dict(CustomUser.ROLE_CHOICES).keys():
#                     user.role = new_role
#                     user.save()
#                     return redirect("super_admin_dashboard:users_list")
#             except ValueError:
#                 pass  # Ignore invalid input
#     return render(request, "map_role.html", {"user": user, "roles": CustomUser.ROLE_CHOICES})







# # ////////////////////////////      CALENDAR SET UP     ///////////////////////////////////


# import json
# from datetime import date, datetime, timedelta

# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
# from django.views.decorators.http import require_POST, require_GET
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.utils.dateparse import parse_date
# from django.template.loader import get_template


# from .models import State, District, LocalBody, LocalBodyCalendar
# from .utils import is_super_admin





# @login_required
# @user_passes_test(is_super_admin)
# def calendar_view(request):
#     """Main page where admin picks state/district/localbody and sees FullCalendar."""
#     states = State.objects.all().order_by("name")
#     return render(request, "calendar.html", {"states": states})


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_districts(request, state_id):
#     districts = District.objects.filter(state_id=state_id).values("id", "name")
#     return JsonResponse(list(districts), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_localbodies(request, district_id):
#     lbs = LocalBody.objects.filter(district_id=district_id).values("id", "name", "body_type")
#     return JsonResponse(list(lbs), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_wards(request, localbody_id):
#     """Load wards for a specific localbody"""
#     try:
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         # Convert to the format expected by the frontend
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# # Test endpoint without authentication for debugging
# def debug_wards_no_auth(request, localbody_id):
#     """Debug endpoint to test ward loading without authentication"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         wards_data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         print(f"DEBUG NO AUTH: Loading wards for localbody_id {localbody_id}")
#         print(f"DEBUG NO AUTH: Found {len(wards_data)} wards")
#         print(f"DEBUG NO AUTH: Sample data: {wards_data[:2] if wards_data else 'None'}")
#         return JsonResponse(wards_data, safe=False)
#     except LocalBody.DoesNotExist:
#         return JsonResponse({"error": "Local body not found"}, status=404)
#     except Exception as e:
#         print(f"DEBUG NO AUTH: Error: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates(request, localbody_id):
#     events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#     # FullCalendar expects events with at least id and start
#     data = [{"id": e["id"], "title": "Assigned", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates_by_ward(request, localbody_id):
#     """Get calendar dates filtered by ward number"""
#     ward_number = request.GET.get('ward')
#     if ward_number:
#         # For now, we'll return all calendar dates for the localbody
#         # In a more advanced implementation, you might have ward-specific calendar entries
#         events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#         data = [{"id": e["id"], "title": f"Assigned - Ward {ward_number}", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     else:
#         data = []
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def create_calendar_date(request, localbody_id):
#     """Create one date or range. Expects 'date' in YYYY-MM-DD or 'start' & 'end' for ranges."""
#     lb = get_object_or_404(LocalBody, pk=localbody_id)

#     # support single-date or start/end
#     start = request.POST.get("start")
#     end = request.POST.get("end")
#     single = request.POST.get("date")

#     created = []
#     if single:
#         d = parse_date(single)
#         if not d:
#             return HttpResponseBadRequest("Invalid date")
#         entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=d)
#         if created_flag:
#             created.append({"id": entry.id, "date": entry.date.isoformat()})
#         return JsonResponse({"status": "created", "created": created})

#     if start and end:
#         s = parse_date(start)
#         e = parse_date(end)
#         if not s or not e:
#             return HttpResponseBadRequest("Invalid start/end")
#         cur = s
#         while cur <= e:
#             entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=cur)
#             if created_flag:
#                 created.append({"id": entry.id, "date": entry.date.isoformat()})
#             cur += timedelta(days=1)
#         return JsonResponse({"status": "created_range", "created": created})

#     return HttpResponseBadRequest("Provide 'date' or 'start' and 'end'.")


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def update_calendar_date(request, pk):
#     """Change date for an existing LocalBodyCalendar entry. Expect 'new_date' YYYY-MM-DD"""
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     new_date_raw = request.POST.get("new_date")
#     if not new_date_raw:
#         return HttpResponseBadRequest("Missing new_date")
#     new_date = parse_date(new_date_raw.split("T")[0])
#     if not new_date:
#         return HttpResponseBadRequest("Invalid date")
#     # prevent duplicates: if another entry exists for that localbody on same date -> reject
#     exists = LocalBodyCalendar.objects.filter(localbody=entry.localbody, date=new_date).exclude(pk=entry.pk).exists()
#     if exists:
#         return JsonResponse({"status": "conflict", "message": "Date already assigned"}, status=409)
#     entry.date = new_date
#     entry.save()
#     return JsonResponse({"status": "updated", "id": entry.id, "date": entry.date.isoformat()})


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def delete_calendar_date(request, pk):
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     entry.delete()
#     return JsonResponse({"status": "deleted", "id": pk})






# # /////////////// super admin create waste oder


# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser
# from super_admin_dashboard.models import State, District, LocalBody
# @login_required
# def create_waste_profile(request):
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     if request.method == "POST":
#         contact_number = request.POST.get("contact_number")

#         # Step 1: Check if customer exists
#         try:
#             customer = CustomUser.objects.get(contact_number=contact_number, role=0)
#         except CustomUser.DoesNotExist:
#             messages.error(request, "No registered customer found with this contact number.")
#             return redirect("super_admin_dashboard:create_waste_profile")

#         # Step 2: Collect waste info details from form
#         full_name = request.POST.get("full_name")
#         secondary_number = request.POST.get("secondary_number")
#         pickup_address = request.POST.get("pickup_address")
#         landmark = request.POST.get("landmark")
#         pincode = request.POST.get("pincode")
#         state_id = request.POST.get("state")
#         district_id = request.POST.get("district")
#         localbody_id = request.POST.get("localbody")
#         waste_type = request.POST.get("waste_type")
#         number_of_bags = request.POST.get("number_of_bags")
#         ward = request.POST.get("ward")
#         selected_date_id = request.POST.get("selected_date")  # calendar selected date

#         # Step 3: Create Waste Profile
#         waste_info = CustomerWasteInfo.objects.create(
#             user=customer,
#             full_name=full_name,
#             secondary_number=secondary_number,
#             pickup_address=pickup_address,
#             landmark=landmark,
#             pincode=pincode,
#             state_id=state_id,
#             district_id=district_id,
#             localbody_id=localbody_id,
#             waste_type=waste_type,
#             number_of_bags=number_of_bags,
#             ward=ward
#         )

#         # Step 4: Save pickup date if given
#         if selected_date_id:
#             try:
#                 cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                 CustomerPickupDate.objects.create(
#                     user=customer,
#                     waste_info=waste_info,
#                     localbody_calendar=cal
#                 )
#             except LocalBodyCalendar.DoesNotExist:
#                 messages.warning(request, "Invalid pickup date selected.")

#         messages.success(request, f"Waste profile created for {customer.first_name}")
#         return redirect("super_admin_dashboard:view_customer_waste_info")

#     # GET request
#     states = State.objects.all()
#     ward_range = range(1, 74)  # Wards 1–73
#     bag_range = range(1, 11)   # Bags 1–10
#     # For super admin form, we don't have a localbody selected yet, so show numbers only
#     ward_options = get_ward_options(None)

#     return render(request, "superadmin_waste_form.html", {
#         "states": states,
#         "ward_range": ward_range,
#         "bag_range": bag_range,
#         "ward_options": ward_options,
#     })




# from .forms import WasteProfileForm  # we'll create this form



# @login_required
# def view_waste_profile(request, pk):
#     waste_info = get_object_or_404(
#         CustomerWasteInfo.objects.select_related(
#             "user", "state", "district", "localbody", "assigned_collector"
#         ),
#         pk=pk
#     )

#     # pickup dates for this profile
#     pickup_dates = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     return render(request, "superadmin_view_waste.html", {
#         "info": waste_info,
#         "pickup_dates": pickup_dates,
#     })



# @login_required
# def edit_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     existing_pickups = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     if request.method == "POST":
#         form = WasteProfileForm(request.POST, instance=waste_info)
#         if form.is_valid():
#             waste_info = form.save()

#             selected_date_id = request.POST.get("selected_date")
#             if selected_date_id:
#                 try:
#                     cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                     CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={"localbody_calendar": cal}
#                     )
#                 except LocalBodyCalendar.DoesNotExist:
#                     messages.warning(request, "⚠️ Invalid pickup date selected.")

#             messages.success(request, "✅ Waste profile updated successfully.")
#             return redirect("super_admin_dashboard:waste_info_list")
#     else:
#         form = WasteProfileForm(instance=waste_info)

#     available_dates = LocalBodyCalendar.objects.filter(localbody=waste_info.localbody).order_by("date")
#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Debug: Print to console
#     print(f"DEBUG: Districts count: {districts.count()}")
#     print(f"DEBUG: LocalBodies count: {localbodies.count()}")
#     print(f"DEBUG: Selected filters - District: {request.GET.get('district_filter')}, LocalBody: {request.GET.get('localbody_filter')}, Phone: {request.GET.get('phone_filter')}")

#     return render(request, "superadmin_edit_waste.html", {
#         "form": form,
#         "info": waste_info,
#         "existing_pickups": existing_pickups,
#         "available_dates": available_dates,
#         "districts": districts,
#         "localbodies": localbodies
#     })



# @login_required
# def delete_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     if request.method == "POST":
#         waste_info.delete()
#         messages.success(request, "🗑️ Waste profile deleted successfully.")
#         return redirect("super_admin_dashboard:waste_info_list")  # ✅ updated

#     return render(request, "superadmin_confirm_delete.html", {
#         "info": waste_info
#     })


# from django.core.paginator import Paginator
# from django.db.models import Q

# @login_required
# def waste_info_list(request):
#     search_query = request.GET.get("q", "")   # search input
#     page_number = request.GET.get("page", 1)  # current page

#     # Fetch all customer waste profiles
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         "state", "district", "localbody", "assigned_collector", "user"
#     ).prefetch_related("customerpickupdate_set__localbody_calendar")

#     # ✅ Search filter (name / phone / address)
#     if search_query:
#         waste_infos = waste_infos.filter(
#             Q(user__first_name__icontains=search_query) |
#             Q(user__last_name__icontains=search_query) |
#             Q(user__contact_number__icontains=search_query) |
#             Q(pickup_address__icontains=search_query)
#         )

#     # ✅ Pagination (10 profiles per page)
#     paginator = Paginator(waste_infos.order_by("-id"), 10)
#     page_obj = paginator.get_page(page_number)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     return render(request, "waste_info_list.html", {
#         "page_obj": page_obj,
#         "collectors": collectors,
#         "search_query": search_query,
#     })

# @login_required
# @user_passes_test(is_super_admin)
# def load_localbodies_for_reports(request):
#     district_id = request.GET.get('district_id')
#     localbodies = LocalBody.objects.filter(district_id=district_id).values("id", "name") if district_id else []
#     return JsonResponse(list(localbodies), safe=False)

# @login_required
# @user_passes_test(is_super_admin)
# def generate_reports(request):
#     """
#     View to display the reports page.
#     """
#     return render(request, 'reports.html')

# @login_required
# @user_passes_test(is_super_admin)
# def generate_report(request):
#     """Generate various types of reports"""
#     if request.method == 'POST':
#         try:
#             report_type = request.POST.get('report_type')
#             print(f"Generating report type: {report_type}")

#             # Get real data for reports
#             from customer_dashboard.models import CustomerWasteInfo
#             from authentication.models import CustomUser
#             from waste_collector_dashboard.models import WasteCollection
#             from datetime import date, datetime, timedelta

#             # Initialize report data
#             report_data = {
#                 'report_type': report_type,
#                 'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                 'report_name': f"{report_type.replace('_', ' ').title()} Report"
#             }

#             # Generate specific report data based on type
#             if report_type == 'daily_collection':
#                 # Get today's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date=today
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'collections_data': [{
#                         'customer': col.customer.get_full_name() if col.customer else 'Unknown',
#                         'address': col.location,
#                         'waste_type': col.customer.customerwasteinfo_set.first().waste_type if col.customer and col.customer.customerwasteinfo_set.exists() else 'Unknown',
#                         'bags': col.number_of_bags,
#                         'collected_at': col.collection_time.strftime('%H:%M') if col.collection_time else 'N/A'
#                     } for col in collections]
#                 })

#             elif report_type == 'weekly_collection':
#                 # Get this week's collections
#                 today = date.today()
#                 week_start = today - timedelta(days=today.weekday())
#                 week_end = week_start + timedelta(days=6)

#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__range=[week_start, week_end]
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
#                 })

#             elif report_type == 'monthly_collection':
#                 # Get this month's collections
#                 today = date.today()
#                 collections = WasteCollection.objects.filter(
#                     scheduled_date__year=today.year,
#                     scheduled_date__month=today.month
#                 ).select_related('customer', 'localbody')

#                 report_data.update({
#                     'total_collections': collections.count(),
#                     'total_bags': sum(col.number_of_bags for col in collections),
#                     'period': today.strftime('%B %Y')
#                 })

#             elif report_type == 'customer_summary':
#                 # Get customer summary data
#                 customers = CustomUser.objects.filter(role=0)
#                 total_customers = customers.count()
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).count()

#                 report_data.update({
#                     'total_customers': total_customers,
#                     'active_customers': active_customers,
#                     'new_customers_this_month': active_customers
#                 })

#             elif report_type == 'active_customers':
#                 # Get active customers
#                 active_customers = CustomerWasteInfo.objects.filter(
#                     created_at__gte=date.today() - timedelta(days=30)
#                 ).select_related('user', 'state', 'district', 'localbody')

#                 report_data.update({
#                     'total_active_customers': active_customers.count(),
#                     'customer_list': [{
#                         'name': info.user.get_full_name() if info.user else 'Unknown',
#                         'phone': info.user.contact_number if hasattr(info.user, 'contact_number') else 'N/A',
#                         'address': info.pickup_address if hasattr(info, 'pickup_address') else 'N/A',
#                         'waste_type': info.waste_type,
#                         'status': info.status,
#                         'last_collection': 'N/A',
#                         'days_since_last': 'N/A'
#                     } for info in active_customers]
#                 })

#             elif report_type == 'payment_analysis':
#                 report_data.update({
#                     'payment_analysis': 'Payment analysis data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'outstanding_payments':
#                 report_data.update({
#                     'outstanding_payments': 'Outstanding payments data',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'collector_performance':
#                 # Analyze collector performance
#                 collectors = CustomUser.objects.filter(role=1)
#                 performance_data = []

#                 for collector in collectors:
#                     try:
#                         # Get collections for this collector this month
#                         collector_collections = WasteCollection.objects.filter(
#                             collector=collector,
#                             scheduled_date__month=date.today().month,
#                             scheduled_date__year=date.today().year
#                         )

#                         total_collections = collector_collections.count()
#                         total_bags = sum(col.number_of_bags for col in collector_collections)

#                         performance_data.append({
#                             'collector_name': collector.get_full_name(),
#                             'total_collections': total_collections,
#                             'total_bags': total_bags,
#                             'days_worked': len(set(col.scheduled_date for col in collector_collections if col.scheduled_date)),
#                         })
#                     except Exception as e:
#                         print(f"Error processing collector {collector.id}: {e}")
#                         continue

#                 # Sort by performance
#                 performance_data.sort(key=lambda x: x['total_collections'], reverse=True)

#                 report_data.update({
#                     'period': date.today().strftime('%B %Y'),
#                     'total_collectors': len(collectors),
#                     'performance_data': performance_data,
#                     'top_performers': performance_data[:5]
#                 })

#             elif report_type == 'efficiency_metrics':
#                 report_data.update({
#                     'efficiency_metrics': 'Operational efficiency metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             elif report_type == 'service_level':
#                 report_data.update({
#                     'service_level': 'Service level metrics',
#                     'period': date.today().strftime('%B %Y')
#                 })

#             else:
#                 return JsonResponse({'success': False, 'error': f'Unknown report type: {report_type}'}, status=400)

#             print("Report generated successfully:", report_data)
#             return JsonResponse({
#                 'success': True,
#                 'report_data': report_data,
#                 'report_name': report_data['report_name']
#             })

#         except Exception as e:
#             error_msg = str(e)
#             print("Error generating report:", error_msg)
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'success': False, 'error': error_msg}, status=500)

#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# @login_required
# @user_passes_test(is_super_admin)
# def load_districts_for_reports(request):
#     state_id = request.GET.get('state_id')
#     districts = District.objects.filter(state_id=state_id).values("id", "name") if state_id else []
#     return JsonResponse(list(districts), safe=False)


#   # Get additional data for CRUD functionality
#     from authentication.models import CustomUser
#     from super_admin_dashboard.models import LocalBody

#     all_customers = CustomUser.objects.filter(role=0)  # Customers
#     all_localbodies = LocalBody.objects.all()

#     try:
#         response = render(request, 'view_collected_data.html', {
#             'all_data': all_data,
#             'all_customers': all_customers,
#             'all_localbodies': all_localbodies,
#         })
#         print("Template rendered successfully")
#         print("=======================================")
#         return response
#     except Exception as e:
#         print(f"ERROR rendering template: {e}")
#         import traceback
#         traceback.print_exc()
#         raise


# # CRUD Operations for Waste Collection
# @login_required
# @user_passes_test(can_view_collected_data)
# def update_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)

#         # Update fields based on POST data
#         waste_collection.ward = request.POST.get('ward', waste_collection.ward)
#         waste_collection.location = request.POST.get('location', waste_collection.location)
#         waste_collection.number_of_bags = request.POST.get('number_of_bags', waste_collection.number_of_bags)
#         waste_collection.building_no = request.POST.get('building_no', waste_collection.building_no)
#         waste_collection.street_name = request.POST.get('street_name', waste_collection.street_name)
#         waste_collection.kg = request.POST.get('kg', waste_collection.kg)

#         # Handle customer and localbody foreign keys
#         if request.POST.get('customer'):
#             customer_id = int(request.POST.get('customer'))
#             waste_collection.customer = CustomUser.objects.get(id=customer_id, role=0)

#         if request.POST.get('localbody'):
#             localbody_id = int(request.POST.get('localbody'))
#             waste_collection.localbody = LocalBody.objects.get(id=localbody_id)

#         # Handle date fields
#         scheduled_date_str = request.POST.get('scheduled_date')
#         if scheduled_date_str:
#             waste_collection.scheduled_date = scheduled_date_str
#         elif scheduled_date_str == '':
#             waste_collection.scheduled_date = None

#         # Handle time field
#         collection_time_str = request.POST.get('collection_time')
#         if collection_time_str:
#             from datetime import datetime
#             time_obj = datetime.strptime(collection_time_str, '%H:%M').time()
#             waste_collection.collection_time = time_obj
#         elif collection_time_str == '':
#             waste_collection.collection_time = None

#         # Recalculate total amount if kg or rate changes
#         waste_collection.save()

#         return JsonResponse({'success': True, 'message': 'Record updated successfully'})

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected customer does not exist'})
#     except LocalBody.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Selected local body does not exist'})
#     except ValueError as e:
#         return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})


# @login_required
# @user_passes_test(can_view_collected_data)
# def delete_waste_collection(request, pk):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

#     try:
#         waste_collection = get_object_or_404(WasteCollection, pk=pk)
#         waste_collection.delete()
#         return JsonResponse({'success': True, 'message': 'Record deleted successfully'})

#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})







# @login_required
# @user_passes_test(is_super_admin)
# def export_all_users_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"all_users_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Role', 'Contact Number', 'Date Joined'])

#     users = CustomUser.objects.all().order_by('id')

#     for user in users:
#         writer.writerow([
#             user.id,
#             user.username,
#             user.first_name,
#             user.last_name,
#             user.email,
#             user.get_role_display(),
#             user.contact_number,
#             user.date_joined.strftime("%Y-%m-%d %H:%M") if user.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_customers_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"customers_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     customers = CustomUser.objects.filter(role=0)

#     for customer in customers:
#         writer.writerow([
#             customer.id,
#             customer.username,
#             customer.first_name,
#             customer.last_name,
#             customer.email,
#             customer.contact_number,
#             customer.date_joined.strftime("%Y-%m-%d %H:%M") if customer.date_joined else 'N/A'
#         ])

#     return response

# @login_required
# @user_passes_test(is_super_admin)
# def export_collectors_csv(request):
#     import csv
#     from django.http import HttpResponse
#     from datetime import datetime

#     response = HttpResponse(content_type='text/csv')
#     filename = f"collectors_report_{datetime.now().strftime('%Y%m%d')}.csv"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Date Joined'])

#     collectors = CustomUser.objects.filter(role=1)

#     for collector in collectors:
#         writer.writerow([
#             collector.id,
#             collector.username,
#             collector.first_name,
#             collector.last_name,
#             collector.email,
#             collector.contact_number,
#             collector.date_joined.strftime("%Y-%m-%d %H:%M") if collector.date_joined else 'N/A'
#         ])

#     return response


# # Test endpoint for debugging with authentication
# @login_required
# @user_passes_test(is_super_admin)
# def test_wards_endpoint(request, localbody_id):
#     """Test endpoint to verify ward loading is working"""
#     try:
#         # Since Ward model doesn't exist, return static ward data
#         localbody = LocalBody.objects.get(id=localbody_id)
#         ward_options = get_ward_options(localbody.name)
#         data = [{"ward_number": option[0], "ward_name": option[1]} for option in ward_options]
#         return JsonResponse({
#             "status": "success",
#             "localbody_id": localbody_id,
#             "localbody_name": localbody.name,
#             "ward_count": len(data),
#             "wards": data
#         })
#     except LocalBody.DoesNotExist:
#         return JsonResponse({
#             "status": "error",
#             "message": "Local body not found"
#         }, status=404)
#     except Exception as e:
#         return JsonResponse({
#             "status": "error",
#             "message": str(e)
#         }, status=500)


# # Price Control Views
# @login_required
# @user_passes_test(is_super_admin)
# def price_control(request):
#     """Price control page for managing waste collection pricing"""
#     from .models import District, LocalBody, WasteTypePrice, ServiceFee, LocationPriceMultiplier

#     districts = District.objects.all().order_by('name')
#     localbodies = LocalBody.objects.all().order_by('name')

#     # Get existing pricing data
#     waste_prices = WasteTypePrice.objects.all()
#     service_fee = ServiceFee.objects.first()
#     location_multipliers = LocationPriceMultiplier.objects.select_related('district', 'localbody').all()

#     context = {
#         'districts': districts,
#         'localbodies': localbodies,
#         'waste_prices': waste_prices,
#         'service_fee': service_fee,
#         'location_multipliers': location_multipliers,
#     }
#     return render(request, 'price_control.html', context)


# @login_required
# @user_passes_test(is_super_admin)
# def load_price_history(request):
#     """Load price history for display"""
#     if request.method == 'GET':
#         try:
#             from .models import PriceHistory
#             from django.core.serializers.json import DjangoJSONEncoder

#             history = PriceHistory.objects.select_related('updated_by').order_by('-created_at')[:20]

#             history_data = []
#             for item in history:
#                 history_data.append({
#                     'date': item.created_at.strftime('%Y-%m-%d %H:%M'),
#                     'type': item.pricing_type.replace('_', ' ').title(),
#                     'category': item.category,
#                     'old_price': f"₹{item.old_value}" if item.old_value else '-',
#                     'new_price': f"₹{item.new_value}" if item.new_value else '-',
#                     'updated_by': item.updated_by.get_full_name() if item.updated_by else 'System',
#                     'status': 'active' if item.action_type == 'create' else 'updated'
#                 })

#             return JsonResponse({
#                 'success': True,
#                 'data': history_data
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_waste_price(request):
#     """Save waste type pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import WasteTypePrice, PriceHistory
#             data = json.loads(request.body)

#             waste_type = data.get('waste_type')
#             price_per_kg = data.get('price_per_kg')
#             status = data.get('status', 'active')

#             # Validate input
#             if not waste_type or price_per_kg is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             price_per_kg = float(price_per_kg)
#             if price_per_kg < 0:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price must be non-negative'
#                 })

#             # Get or create waste type price
#             waste_price, created = WasteTypePrice.objects.get_or_create(
#                 waste_type=waste_type,
#                 defaults={
#                     'price_per_kg': price_per_kg,
#                     'status': status,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_price = waste_price.price_per_kg
#                 waste_price.price_per_kg = price_per_kg
#                 waste_price.status = status
#                 waste_price.updated_by = request.user
#                 waste_price.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     old_value=old_price,
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='waste_type',
#                     category=waste_price.get_waste_type_display(),
#                     new_value=price_per_kg,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Waste type price saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_service_fees(request):
#     """Save service fee pricing"""
#     if request.method == 'POST':
#         try:
#             from .models import ServiceFee, PriceHistory
#             data = json.loads(request.body)

#             base_fee = data.get('base_fee')
#             fee_per_bag = data.get('fee_per_bag')
#             min_charge = data.get('min_charge')

#             # Validate input
#             if base_fee is None or fee_per_bag is None or min_charge is None:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Missing required fields'
#                 })

#             base_fee = float(base_fee)
#             fee_per_bag = float(fee_per_bag)
#             min_charge = float(min_charge)

#             if any(x < 0 for x in [base_fee, fee_per_bag, min_charge]):
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'All fees must be non-negative'
#                 })

#             # Get or create service fee
#             service_fee, created = ServiceFee.objects.get_or_create(
#                 pk=1,  # Assume single service fee record
#                 defaults={
#                     'base_fee': base_fee,
#                     'fee_per_bag': fee_per_bag,
#                     'min_charge': min_charge,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_base_fee = service_fee.base_fee
#                 old_fee_per_bag = service_fee.fee_per_bag
#                 old_min_charge = service_fee.min_charge

#                 service_fee.base_fee = base_fee
#                 service_fee.fee_per_bag = fee_per_bag
#                 service_fee.min_charge = min_charge
#                 service_fee.updated_by = request.user
#                 service_fee.save()

#                 # Log changes to history
#                 if old_base_fee != base_fee:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Base Fee',
#                         old_value=old_base_fee,
#                         new_value=base_fee,
#                         updated_by=request.user
#                     )

#                 if old_fee_per_bag != fee_per_bag:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Fee per Bag',
#                         old_value=old_fee_per_bag,
#                         new_value=fee_per_bag,
#                         updated_by=request.user
#                     )

#                 if old_min_charge != min_charge:
#                     PriceHistory.objects.create(
#                         action_type='update',
#                         pricing_type='service_fee',
#                         category='Minimum Charge',
#                         old_value=old_min_charge,
#                         new_value=min_charge,
#                         updated_by=request.user
#                     )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='service_fee',
#                     category='Service Fees',
#                     new_value=base_fee,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Service fees saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @user_passes_test(is_super_admin)
# def save_location_multiplier(request):
#     """Save location-based price multiplier"""
#     if request.method == 'POST':
#         try:
#             from .models import LocationPriceMultiplier, PriceHistory, District, LocalBody
#             data = json.loads(request.body)

#             # Validate price multiplier
#             price_multiplier = float(data.get('price_multiplier', 0))
#             if price_multiplier > 500.0 or price_multiplier < 0.1:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Price multiplier must be between 0.1 and 500.0'
#                 })

#             district_id = data.get('district')
#             localbody_id = data.get('localbody')

#             if not district_id or not localbody_id:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'District and Local Body are required'
#                 })

#             # Get district and localbody objects
#             district = District.objects.get(id=district_id)
#             localbody = LocalBody.objects.get(id=localbody_id)

#             # Get or create location price multiplier
#             location_multiplier, created = LocationPriceMultiplier.objects.get_or_create(
#                 district=district,
#                 localbody=localbody,
#                 defaults={
#                     'price_multiplier': price_multiplier,
#                     'updated_by': request.user
#                 }
#             )

#             if not created:
#                 # Update existing
#                 old_multiplier = location_multiplier.price_multiplier
#                 location_multiplier.price_multiplier = price_multiplier
#                 location_multiplier.updated_by = request.user
#                 location_multiplier.save()

#                 # Log to history
#                 PriceHistory.objects.create(
#                     action_type='update',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     old_value=old_multiplier,
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )
#             else:
#                 # Log creation to history
#                 PriceHistory.objects.create(
#                     action_type='create',
#                     pricing_type='location_multiplier',
#                     category=f'{localbody.name} - {district.name}',
#                     new_value=price_multiplier,
#                     updated_by=request.user
#                 )

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Location multiplier saved successfully'
#             })
#         except ValueError:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid price multiplier value'
#             })
#         except District.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'District not found'
#             })
#         except LocalBody.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Local Body not found'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})






# @login_required
# def customer_activity_details(request, customer_id):
#     """
#     Show detailed customer activity including waste info and collection history
#     """
#     from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
#     from waste_collector_dashboard.models import WasteCollection
#     from django.db.models import Q, Sum

#     # Get the customer user
#     try:
#         customer = CustomUser.objects.get(id=customer_id, role=0)
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Customer not found')
#         return redirect('super_admin_dashboard:view_customer_waste_info')

#     # Get customer waste info
#     waste_infos = CustomerWasteInfo.objects.filter(
#         user=customer
#     ).select_related(
#         'state', 'district', 'localbody', 'assigned_collector'
#     ).order_by('-created_at')

#     # Get collection history for this customer
#     collection_history = WasteCollection.objects.filter(
#         customer=customer
#     ).select_related(
#         'collector', 'localbody'
#     ).order_by('-created_at')

#     # Get pickup dates
#     pickup_dates = CustomerPickupDate.objects.filter(
#         user=customer
#     ).select_related(
#         'localbody_calendar', 'waste_info'
#     ).order_by('-created_at')

#     # Calculate statistics
#     total_collections = collection_history.count()
#     total_kg_collected = collection_history.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     total_amount_paid = collection_history.aggregate(
#         total_amount=Sum('total_amount')
#     )['total_amount'] or 0

#     # Recent activity (last 10 items from both waste info and collections)
#     recent_waste_info = waste_infos[:5]
#     recent_collections = collection_history[:5]

#     context = {
#         'customer': customer,
#         'waste_infos': waste_infos,
#         'collection_history': collection_history,
#         'pickup_dates': pickup_dates,
#         'total_collections': total_collections,
#         'total_kg_collected': total_kg_collected,
#         'total_amount_paid': total_amount_paid,
#         'recent_waste_info': recent_waste_info,
#         'recent_collections': recent_collections,
#     }

#     return render(request, 'customer_activity_details.html', context)


# @login_required
# def collector_activity_details(request, collector_id):
#     """
#     Show detailed collector activity including collection history and assigned customers
#     """
#     from customer_dashboard.models import CustomerWasteInfo
#     from waste_collector_dashboard.models import WasteCollection
#     from django.db.models import Q, Sum, Count

#     # Get the collector user
#     try:
#         collector = CustomUser.objects.get(id=collector_id, role=1)
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Collector not found')
#         return redirect('super_admin_dashboard:view_collected_data')

#     # Get collection history for this collector
#     collection_history = WasteCollection.objects.filter(
#         collector=collector
#     ).select_related(
#         'customer', 'localbody'
#     ).order_by('-created_at')

#     # Get assigned customers to this collector
#     assigned_customers = CustomerWasteInfo.objects.filter(
#         assigned_collector=collector
#     ).select_related(
#         'user', 'state', 'district', 'localbody'
#     ).order_by('-created_at')

#     # Calculate statistics
#     total_collections = collection_history.count()
#     total_kg_collected = collection_history.aggregate(
#         total_kg=Sum('kg')
#     )['total_kg'] or 0

#     total_amount_collected = collection_history.aggregate(
#         total_amount=Sum('total_amount')
#     )['total_amount'] or 0

#     total_customers_assigned = assigned_customers.count()

#     # Recent activity
#     recent_collections = collection_history[:10]
#     recent_assigned_customers = assigned_customers[:5]

#     # Payment method statistics
#     payment_stats = collection_history.values('payment_method').annotate(
#         count=Count('id')
#     ).order_by('-count')

#     context = {
#         'collector': collector,
#         'collection_history': collection_history,
#         'assigned_customers': assigned_customers,
#         'total_collections': total_collections,
#         'total_kg_collected': total_kg_collected,
#         'total_amount_collected': total_amount_collected,
#         'total_customers_assigned': total_customers_assigned,
#         'recent_collections': recent_collections,
#         'recent_assigned_customers': recent_assigned_customers,
#         'payment_stats': payment_stats,
#     }

#     return render(request, 'collector_activity_details.html', context)




#  # --- Notifications for super admin dashboard (latest admin_home) ---
#     from datetime import timedelta
#     cutoff_date = timezone.now() - timedelta(days=60)
#     Notification.objects.filter(user=request.user, created_at__lt=cutoff_date).delete()

#     # Pending orders notification
#     Notification.create_pending_order_notification(
#         user=request.user,
#         order_count=pending_orders,
#     )

#     # Collection rate notification
#     Notification.create_collection_rate_notification(
#         user=request.user,
#         rate=collection_rate
#     )

#     # Milestone notification when completed orders reach certain thresholds
#     if completed_orders >= 50:
#         milestone_title = "50+ Orders Completed"
#         description = f"You have successfully completed {completed_orders} waste collection orders."
#         if not Notification.objects.filter(
#             user=request.user,
#             title__icontains=milestone_title
#         ).exists():
#             Notification.create_milestone_notification(
#                 user=request.user,
#                 milestone_title=milestone_title,
#                 description=description
#             )

#     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]


