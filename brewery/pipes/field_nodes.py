import base
import re
import copy
import brewery.ds as ds

class FieldMapNode(base.Node):
    """Node renames input fields or drops them from the stream.
    """
    __node_info__ = {
        "type": "field",
        "label" : "Field Map",
        "description" : "Rename or drop fields from the stream.",
        "attributes" : [
            {
                "name": "map_fields",
                "label": "Map fields",
                "description": "Dictionary of input to output field name."
            },
            {
                "name": "drop_fields",
                "label": "drop fields",
                "description": "List of fields to be dropped from the stream."
            }
        ]
    }

    def __init__(self, map_fields = None, drop_fields = None):
        super(FieldMapNode, self).__init__()
        if map_fields:
            self.mapped_fields = map_fields
        else:
            self.mapped_fields = {}

        if drop_fields:
            self.dropped_fields = set(drop_fields)
        else:
            self.dropped_fields = set([])
        
    def rename_field(self, source, target):
        """Change field name"""
        self.mapped_fields[source] = target
    
    def drop_field(self, field):
        """Do not pass field from source to target"""
        self.dropped_fields.add(field)

    @property
    def output_fields(self):
        output_fields = ds.FieldList()
        
        for field in self.input.fields:
            if field.name in self.mapped_fields:
                # Create a copy and rename field if it is mapped
                new_field = copy.copy(field)
                new_field.name = self.mapped_fields[field.name]
                output_fields.append(new_field)
            elif field.name not in self.dropped_fields:
                # Pass field if it is not in dropped field list
                output_fields.append(field)
            
        return output_fields

    def run(self):
        self.mapped_field_names = self.mapped_fields.keys()

        # FIXME: change this to row based processing
        for record in self.input.records():
            for field in self.mapped_field_names:
                if field in record:
                    value = record[field]
                    del record[field]
                    record[self.mapped_fields[field]] = value
            for field in self.dropped_fields:
                if field in record:
                    del record[field]
            self.put_record(record)

class TextSubstituteNode(base.Node):
    """Substitute text in a field using regular expression."""
    
    __node_info__ = {
        "type": "field",
        "label" : "Text Substitute",
        "description" : "Substitute text in a field using regular expression.",
        "attributes" : [
            {
                "name": "field",
                "label": "substituted field",
                "description": "Field containing a string or text value where substition will "
                               "be applied"
            },
            {
                "name": "derived_field",
                "label": "derived field",
                "description": "Field where substition result will be stored. If not set, then "
                               "original field will be replaced with new value."
            },
            {
                "name": "substitutions",
                "label": "substitutions",
                "description": "List of substitutions: each substition is a two-element tuple "
                               "(`pattern`, `replacement`) where `pattern` is a regular expression "
                               "that will be replaced using `replacement`"
            }
        ]
    }

    def __init__(self, field, derived_field = None):
        """Creates a node for text replacement.
        
        :Attributes:
            * `field`: field to be used for substitution (should contain a string)
            * `derived_field`: new field to be created after substitutions. If set to ``None`` then the
              source field will be replaced with new substituted value. Default is ``None`` - same field
              replacement.
        
        """
        super(TextSubstituteNode, self).__init__()

        self.field = field
        self.derived_field = derived_field
        self.substitutions = []
        
    def add_substitution(self, pattern, repl):
        """Add replacement rule for field.
        
        :Parameters:
            * `pattern` - regular expression to be searched
            * `replacement` - string to be used as replacement, default is empty string
        """

        self.substitutions.append( (re.compile(pattern), repl) )
    
    # FIXME: implement this
    # @property
    # def output_fields(self):
    #     pass
        
    def run(self):
        pipe = self.input

        if self.derived_field:
            append = True
        else:
            append = False

        index = self.input_fields.index(self.field)
            
        for row in pipe.rows():
            value = row[index]
            for (pattern, repl) in self.substitutions:
                value = re.sub(pattern, repl, value)
            if append:
                row.append(value)
            else:
                row[index] = value

            self.put(row)

class ValueThresholdNode(base.Node):
    """Create a field that will refer to a value bin based on threshold(s). Values of `range` type
    can be compared against one or two thresholds to get low/high or low/medium/high value bins.

    *Note: this node is not yet implemented*
    
    The result is stored in a separate field that will be constructed from source field name and
    prefix/suffix.
    
    For example:
        * amount < 100 is low
        * 100 <= amount <= 1000 is medium
        * amount > 1000 is high

    Generated field will be `amount_threshold` and will contain one of three possible values:
    `low`, `medium`, `hight`
    
    Another possible use case might be for binning after data audit: we want to measure null 
    record count and we set thresholds:
        
        * ratio < 5% is ok
        * 5% <= ratio <= 15% is fair
        * ratio > 15% is bad
        
    We set thresholds as ``(0.05, 0.15)`` and values to ``("ok", "fair", "bad")``
        
    """
    
    __node_info__ = {
        "type": "field",
        "label" : "Value Threshold",
        "description" : "Bin values based on a threshold.",
        "attributes" : [
            {
                "name": "field_thresholds",
                "label": "field",
                "description": "Dictionary of range type field names and threshold tuples."
            },
            {
                "name": "bins",
                "label": "bins",
                "description": "Names of bins based on threshold. Default is low, medium, high"
            },
            {
                "name": "prefix",
                "label": "prefix",
                "description": "field prefix to be used"
            },
            {
                "name": "suffix",
                "label": "suffix",
                "description": "field suffix to be used"
            }
        ]
    }

#     def __init__(self, field, low_value = None, high_value = None):
#         """Creates a node for text replacement.
# 
#         :Attributes:
#             * `field`: field to be used for substitution (should contain a string)
#             * `derived_field`: new field to be created after substitutions. If set to ``None`` then the
#               source field will be replaced with new substituted value. Default is ``None`` - same field
#               replacement.
# 
#         """
#         super(TextSubstituteNode, self).__init__()
# 
#         self.field = field
#         self.derived_field = derived_field
#         self.substitutions = []
# 
#         
#     def run(self):
#         index = self.input_fields.index(self.field)
#         for row in self.input.rows():s
#  

class BinningNode(base.Node):
    """Derive a bin/category field from a value.

    *Note: this node is not yet implemented*
    
    Binning modes:
    
    * fixed width (for example: by 100)
    * fixed number of fixed-width bins
    * n-tiles by count or by sum
    * record rank
    
        
    """
    
    __node_info__ = {
        "type": "field",
        "label" : "Binning",
        "icon": "histogram_node",
        "description" : "Derive a field based on binned values (histogram)"
    }
           