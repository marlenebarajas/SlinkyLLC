from django.conf import settings
from django.core.validators import validate_slug
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class State(models.Model):
    state_code = models.CharField(primary_key=True, max_length=2)
    state_name = models.CharField(max_length=30)


class City(models.Model):
    city_name = models.CharField(max_length=40)
    neighborhood_name = models.CharField(max_length=40, blank=True)
    state_code = models.ForeignKey(State, on_delete=models.CASCADE)


class ZipCode(models.Model):
    zip_code = models.CharField(primary_key=True, max_length=5)
    city = models.ForeignKey(City, on_delete=models.CASCADE)


class CuisineType(models.Model):  # to be used in restaurant table: Japanese food, Italian food, fast food, etc.
    cuisine_type_name = models.CharField(max_length=80)


class OpeningHours(models.Model):  # to be used in restaurant table: opening dates, hours.
    # a choices list of week days
    class WeekDays(models.TextChoices):
        MON = 1, "Monday"
        TUE = 2, "Tuesday"
        WED = 3, "Wednesday"
        THU = 4, "Thursday"
        FRI = 5, "Friday"
        SAT = 6, "Saturday"
        SUN = 7, "Sunday"

    open_date = models.PositiveSmallIntegerField(choices=WeekDays.choices)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        ordering = ('open_date', 'opening_time')
        # unique_together: make fields unique when combined together
        unique_together = ('open_date', 'opening_time', 'closing_time')


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=80)
    restaurant_address = models.CharField(max_length=256)
    # slug example: postmates.com/merchant/chronic-tacos-huntington-beach -> 'chronic-tacos-huntington-beach' is a slug
    slug = models.SlugField(validators=[validate_slug], max_length=256, unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=256, unique=True)
    # one restaurant can have multiple features (cuisine type) and vice versa
    features = models.ManyToManyField(CuisineType, blank=True)
    # one restaurant can have multiple opening hours and vice versa
    timing = models.ManyToManyField(OpeningHours)
    image_link = models.ImageField(upload_to='restaurant_images')
    description = models.CharField(max_length=256)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.SET_DEFAULT, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #averafe rating and average price needed


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=256, unique=True)
    phone_number = models.CharField(max_length=10)
    customer_address = models.CharField(max_length=256, blank=True)
    billing_address = models.CharField(max_length=256, blank=True)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.SET_DEFAULT, default=None)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Driver(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=256, unique=True)
    phone_number = models.CharField(max_length=10)
    driver_address = models.CharField(max_length=256)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.SET_DEFAULT, default=None)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class MenuCategory(models.Model):
    category_name = models.CharField(max_length=60)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)

    class Meta:
        # one restaurant won't allow duplicate menu categories
        unique_together = ('category_name', 'restaurant')


class MenuItem(models.Model):
    item_name = models.CharField(max_length=80)
    description = models.CharField(max_length=512)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    ingredients = models.CharField(max_length=512)
    image_link = models.ImageField(upload_to='item_images')
    # optional: choices = models.ManyToManyField(ItemChoices, blank=true)
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_DEFAULT, default=None)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)

    class Meta:
        # one restaurant won't allow duplicate items on menu
        unique_together = ('restaurant', 'item_name')


# comment out: in case further development
# item choices like toppings, options, etc.
# class ItemChoices(models.Model):
#     choice_name = models.CharField(max_length=80)
#     price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
#     restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
#
#     class Meta:
#         # one restaurant won't allow duplicate choices on menu
#         unique_together = ('restaurant', 'choice_name')


class Order(models.Model):
    order_date = models.DateTimeField()
    special_instruction = models.CharField(max_length=512)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.SET_DEFAULT, default=None)


# comment out: in case further development
# class OrderStatus(models.Model):
#     class OrderStatus(models.TextChoices):
#         CANCELED = 'CANCELED', "order has been canceled"
#         FAILED = 'FAILED', "order has been failed"
#         PROCESSED = 'PROCESSED', "order has been processed"
#
#     order_status = models.CharField(choices=OrderStatus.choices)
#     restaurant = models.ForeignKey('Restaurant', on_delete=models.SET_NULL, blank=True, null=True)


class OrderItem(models.Model):
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.SET_DEFAULT, default=None)

    class Meta:
        # one order won't allow duplicate items
        unique_together = ('order', 'item')


class Delivery(models.Model):
    estimate_time = models.TimeField()
    delivered_time = models.DateTimeField(blank=True, null=True)
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    driver = models.OneToOneField('Driver', on_delete=models.SET_DEFAULT, default=None)


# comment out: in case further development
# class DeliveryStatus(models.Model):
#     class DeliveryStatus(models.TextChoices):
#         CANCELED = 'CANCELED', "order has been canceled"
#         FAILED = 'FAILED', "order has been failed"
#         DELIVERED = 'DELIVERED', "order has been delivered"
#
#     delivery_status = models.CharField(choices=DeliveryStatus.choices)


class Payment(models.Model):
    # a choices list of payment methods
    class PaymentMethods(models.TextChoices):
        COD = 'COD', "cash on delivery"
        CARD = 'CARD', "Credit Card"
        PAYPAL = 'PAYPAL', "PayPal"
        GIFTCARD = 'GIFTCARD', "gift card"

    tips = models.DecimalField(max_digits=7, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=7, decimal_places=2)
    sales_tax = models.DecimalField(max_digits=7, decimal_places=2)
    promo_code = models.CharField(max_length=5, unique=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    payment_date = models.DateTimeField()
    billing_address = models.CharField(max_length=256)
    payment_amount = models.DecimalField(max_digits=7, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethods.choices, default=PaymentMethods.CARD)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)


class PaymentInformation(models.Model):
    name_on_card = models.CharField(max_length=256)
    expire_day = models.DateField()
    card_number = models.CharField(max_length=256, unique=True)
    security_code = models.CharField(max_length=256)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Review(models.Model):
    # a choices list of rating
    class RatingChoices(models.TextChoices):
        ONE = 1, "ONE"
        TWO = 2, "TWO"
        THREE = 3, "THREE"
        FOUR = 4, "FOUR"
        FIVE = 5, "FIVE"

    comment = models.CharField(max_length=1000)
    restaurant_rating = models.PositiveSmallIntegerField(choices=RatingChoices.choices)
    driver_rating = models.PositiveSmallIntegerField(choices=RatingChoices.choices)
    comment_date = models.DateTimeField()
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE)
	
class Cart(models.Model):
    '''
    The Cart model that will hold CartEntrys related to a user's unique cart.
    '''
    user = models.ForeignKey('CustomUserManager', on_delete=models.CASCADE) # gives each customer has their unique cart
    menu_items = models.ManyToManyField(MenuItem, blank=True)
    total_cost = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    order_date = models.DateField(null=True)
    
    
    def add_menu_item(self, menu_item_id):
    '''
    Adds a menu item to a user's cart.
    '''
    try:
        item = MenuItem.objects.get(pk=menu_item_id) # will access the MenuItem that user is trying to add to cart
        try: # if the cart entry already exists, just increment that item's quantity
            item_exists = CartEntry.objects.get(cart=self, menu_item=item)
            item_exists.quantity +=1
            item.exists.save()
        except CartEntry.DoesNotExist: # create a new cart entry with this item
            new_entry = CartEntry.objects.create(cart=self, menu_item=item, quantity=1)
            new_entry.save()
    except ObjectDoesNotExist: # checks that the item is reachable
        pass
    
    
    
    def remove_menu_item:
    '''
    Removes a menu item from a user's cart.
    '''
    try:
        item = MenuItem.objects.get(pk=menu_item_id) # will access the MenuItem that user is trying to add to cart
        try: # if the cart entry already exists, just decrement that item's quantity
            item_exists = CartEntry.objects.get(cart=self, menu_item=item)
            item_exists.quantity-=1
            item_exists.save()
            if item_exists.quantity=0: # if the quantity is 0, delete CartEntry
                item_exists.delete()
        except CartEntry.DoesNotExist: # this shouldn't be encountered, but if so
            pass
    except ObjectDoesNotExist: # checks that the item is reachable
        pass
    
    
    def checkout:
    '''
    Creates an Order from the CartEntrys in the user's cart.
    '''
    new_order = Order.objects.create(order_date=this.order_date)
    
    
class CartEntry(models.Model):
    '''
    Cart entry that is linked to a specific user's cart (ForeignKey cart).
    '''
    cart = models.ForeignKey(Cart, null=True, on_delete='CASCADE')
    menu_item = models.ForeignKey(MenuItem, null=True, on_delete='CASCADE')
    quantity = models.PositiveIntegerField()
