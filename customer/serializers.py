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



class CustomerSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        exclude = ['is_deleted', 'is_staff', 'is_superuser', 'groups', 'user_permissions']
        read_only_fields = ['id', 'username', 'email' , 'is_staff', 'is_superuser']

    def get_addresses(self, obj):
        user = self.context['request'].user
        if user.is_staff or user.is_superuser:
            active_addresses = obj.addresses.all()
        else:
            active_addresses = obj.addresses.filter(is_deleted=False)
        return AddressSerializer(active_addresses, many=True).data



class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'username', 'email', 'password',
            'first_name', 'last_name',
            'phone', 'is_seller', 'picture'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def to_internal_value(self, data):
        forbidden = ['is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions']
        for field in forbidden:
            if field in data:
                raise serializers.ValidationError({field: f"You may not set '{field}' during registration."})
        return super().to_internal_value(data)

    def create(self, validated_data):
        return Customer.objects.create_user(**validated_data)
