from rest_framework import serializers
from customer.models import Customer, Address


class AddressCreateSerializer(serializers.ModelSerializer): # for create/update addresses
    class Meta:
        model = Address
        exclude = ['user', 'is_deleted'] # to set user automatically

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class AddressSerializer(serializers.ModelSerializer): # for list/view addresses
    class Meta:
        model = Address
        exclude = ['is_deleted', 'user']
        read_only_fields = ('user',)



class CustomerSerializer(serializers.ModelSerializer): # for customer info and nested list of addresses
    addresses = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        exclude = ['is_deleted']
        read_only_fields = ['id', 'username', 'email', 'is_seller']


    def get_addresses(self, obj):
        user = self.context['request'].user
        if user.is_staff or user.is_superuser:
            active_addresses = obj.addresses.all()
        else:
            active_addresses = obj.addresses.filter(is_deleted=False)
        return AddressSerializer(active_addresses, many=True).data


class CustomerCreateSerializer(serializers.ModelSerializer): # for registration
    class Meta:
        model = Customer
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'is_seller', 'picture']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Customer.objects.create_user(**validated_data) # for secure hashing
