import logging
import xml.etree.ElementTree as ET
import netaddr

from pytos.common.base_types import XML_Object_Base, SubclassWithIdentifierRegistry
from pytos.common.definitions import XML_Tags
from pytos.common.functions import str_to_bool, XML_LOGGER_NAME
from pytos.common.functions.XML import get_xml_text_value, get_xml_int_value

logger = logging.getLogger(XML_LOGGER_NAME)


class Base_Object(XML_Object_Base):
    def __init__(self, xml_tag, display_name, is_global, object_id, name, object_type, application_id=None):
        self.id = object_id
        self.name = name
        self.type = object_type
        self.display_name = display_name
        self.global_ = is_global
        self.application_id = application_id
        super().__init__(xml_tag)
        self.set_attrib(XML_Tags.NAMESPACE_FIELD_ATTRIB_CONTENT, XML_Tags.XSI_NAMESPACE_URL)

    def __hash__(self):
        return hash(self.id)

    def is_global(self):
        return str_to_bool(self.global_)

    def _key(self):
        return self.id, self.name, self.type, self.display_name, self.global_, self.application_id


class Base_Link_Target(XML_Object_Base):
    def __init__(self, xml_tag, connection_id, display_name, name, link):
        self.id = connection_id
        self.display_name = display_name
        self.name = name
        self.link = link
        super().__init__(xml_tag)

    def get_reference_link(self):
        return self.link.get_attrib(XML_Tags.Attributes.HREF)

    def _key(self):
        return self.display_name, self.name, self.link, self.id


class Base_Service(Base_Object):
    def __init__(self, display_name, is_global, service_id, name, service_type, uid, application_id=None):
        self.uid = uid
        super().__init__(XML_Tags.Elements.SERVICE, display_name, is_global, service_id, name, service_type,
                         application_id)

    @classmethod
    def from_xml_node(cls, xml_node):
        """
        Initialize the object from a XML node.
        :param xml_node: The XML node from which all necessary parameters will be parsed.
        :type xml_node: xml.etree.Element
        """
        display_name = get_xml_text_value(xml_node, XML_Tags.Elements.DISPLAY_NAME)
        is_global = get_xml_text_value(xml_node, XML_Tags.Elements.GLOBAL)
        service_id = get_xml_int_value(xml_node, XML_Tags.Elements.ID)
        name = get_xml_text_value(xml_node, XML_Tags.Elements.NAME)
        service_type = get_xml_text_value(xml_node, XML_Tags.Elements.TYPE)
        uid = get_xml_text_value(xml_node, XML_Tags.Elements.UID)
        application_id = get_xml_int_value(xml_node, XML_Tags.Elements.APPLICATION_ID)
        return cls(display_name, is_global, service_id, name, service_type, uid, application_id)


class URL_Link(XML_Object_Base):
    def __init__(self, url):
        super().__init__(XML_Tags.Elements.LINK)
        self.set_attrib(XML_Tags.NAMESPACE_FIELD_ATTRIB_CONTENT, XML_Tags.XSI_NAMESPACE_URL)
        self.set_attrib(XML_Tags.Attributes.HREF, url)

    @classmethod
    def from_xml_node(cls, xml_node):
        """
        Initialize the object from a XML node.
        :param xml_node: The XML node from which all necessary parameters will be parsed.
        :type xml_node: xml.etree.Element
        """
        url = xml_node.attrib[XML_Tags.Attributes.HREF]
        return cls(url)


class Network_Object(Base_Object, metaclass=SubclassWithIdentifierRegistry):
    def __init__(self, xml_tag, display_name, is_global, object_id, name, object_type, attr_type, application_id=None):
        super().__init__(xml_tag, display_name, is_global, object_id, name, object_type, application_id)
        self.set_attrib(XML_Tags.Attributes.XSI_TYPE, attr_type)

    def as_netaddr_obj(self):
        raise NotImplementedError

    def as_netaddr_set(self):
        """This returns a netaddr set representing the Network_Object"""
        return netaddr.IPSet(self.as_netaddr_obj())

    def __hash__(self):
        return hash(str(self.id))

    @staticmethod
    def from_xml_string_auto_type(xml_string):
        xml_node = ET.fromstring(xml_string)
        return Network_Object.from_xml_node_auto_type(xml_node)

    @classmethod
    def from_xml_node_auto_type(cls, xml_node):
        try:
            network_object_type = xml_node.attrib[XML_Tags.Attributes.XSI_NAMESPACE_TYPE]
        except KeyError:
            raise ValueError("XML Node is missing type attribute")
        try:
            return cls.registry[network_object_type].from_xml_node(xml_node)
        except KeyError:
            raise ValueError("Unknown network object type {}".format(network_object_type))


class Service_Object(Base_Object, metaclass=SubclassWithIdentifierRegistry):
    def __init__(self, xml_tag, display_name, is_global, object_id, name, object_type, attr_type, application_id=None):
        super().__init__(xml_tag, display_name, is_global, object_id, name, object_type, application_id)
        self.set_attrib(XML_Tags.Attributes.XSI_TYPE, attr_type)

    def __hash__(self):
        return hash(str(self.id))

    def as_service_type(self):
        raise NotImplementedError

    @staticmethod
    def from_xml_string_auto_type(xml_string):
        xml_node = ET.fromstring(xml_string)
        return Network_Object.from_xml_node_auto_type(xml_node)

    @classmethod
    def from_xml_node_auto_type(cls, xml_node):
        try:
            service_type = xml_node.attrib[XML_Tags.Attributes.XSI_NAMESPACE_TYPE]
        except KeyError:
            raise ValueError("XML Node is missing type attribute")
        try:
            return cls.registry[service_type].from_xml_node(xml_node)
        except KeyError:
            raise ValueError("Unknown network object type {}".format(service_type))