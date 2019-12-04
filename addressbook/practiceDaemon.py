from addressbook.addressbook_pb2 import AddressBook, Person

address_book = AddressBook()
address1 = address_book.people.add()
address1.name = "Jack"
address1.id = 123
address1.email = "jack@126.com"
home_phone_number_jack = address1.phones.add()
home_phone_number_jack.number = "1234567"
home_phone_number_jack.type = Person.HOME
address2 = address_book.people.add(name="rose", id=456,
                                   email="rose@yahoo.com")
home_phone_number_rose = address2.phones.add(number="7654321", type=Person.HOME)
# print(address1)
print(address_book)
