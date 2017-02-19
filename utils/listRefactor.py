from enum import Enum





class BadOrNoneInListRule(Enum):
    remove = 0      # [None] --> [],        [bad] --> []
    none_value = 1  # [None] --> [None],    [bad] --> [None]
    bad_value = 2   # [None] --> [bad],     [bad] --> [bad]

class EmptyListRule(Enum):
    none_value = 0       # None
    bad_value = 1        # bad
    keep_empty_list = 2  # []

class OneElementListRule(Enum):
    follow_list_rule = 0  # keep_list or first_value or concat_value
    first_value = 1       # list[0]

class ListRule(Enum):
    keep_list = 0       # list
    first_value = 1     # list[0]
    reduce_value = 2    # reduce( lambda_func, list)





def list_in_dict_refactor(dictionary, key, list_conversion):
    # type: (dict, list, ListRefactor, str) -> dict
    ret = None
    if key in dictionary.keys():
        val_list = dictionary[key]
        ret = list_conversion.convert(val_list)

        # if isinstance(dictionary[key], list):
        #     val_list = dictionary[key]
        #     ret = list_conversion.convert(val_list)
        # else:
        #     ret = dictionary[key]
    return ret




class ListRefactor:
    # def __init__(self):
    #     self._empty_list_rule = EmptyListRule.none_value
    #     self._bad_or_none_in_list_rule = BadOrNoneInListRule.remove
    #     self._one_element_list_rule = OneElementListRule.follow_list_rule
    #     self._list_rule = ListRule.keep_list
    #
    #     self.bad_value = None
    #     self.list_reducer_func = lambda x, y: str(x) + "\n" + str(y)

    def __init__(self,
                 list_rule=ListRule.keep_list,
                 one_element_rule=OneElementListRule.follow_list_rule,
                 bad_rule=BadOrNoneInListRule.remove,
                 empty_rule=EmptyListRule.none_value,
                 list_reducer_func=lambda x, y: str(x) + "\n" + str(y),
                 bad_value="<bad_value>"):
        self._list_rule = list_rule
        self._one_element_list_rule = one_element_rule
        self._bad_or_none_in_list_rule = bad_rule
        self._empty_list_rule = empty_rule
        self.bad_value = bad_value
        self.list_reducer_func = list_reducer_func

    def setRules(self, list_rule=None, one_element_rule=None, bad_rule=None, empty_rule=None):
        if list_rule is not None:
            self.list_rule = list_rule
        if one_element_rule is not None:
            self.one_element_list_rule = one_element_rule
        if bad_rule is not None:
            self.bad_or_none_in_list_rule = bad_rule
        if empty_rule is not None:
            self.empty_list_rule = empty_rule

    @property
    def bad_or_none_in_list_rule(self):
        return self._bad_or_none_in_list_rule
    @bad_or_none_in_list_rule.setter
    def bad_or_none_in_list_rule(self, rule): # type: (BadOrNoneInListRule) -> None
        self._bad_or_none_in_list_rule = rule

    @property
    def empty_list_rule(self):
        return self._empty_list_rule
    @empty_list_rule.setter
    def empty_list_rule(self, rule): # type: (EmptyListRule) -> None
        self._empty_list_rule = rule


    @property
    def one_element_list_rule(self):
        return self._one_element_list_rule
    @one_element_list_rule.setter
    def one_element_list_rule(self, rule): # type: (OneElementListRule) -> None
        self._one_element_list_rule = rule

    @property
    def list_rule(self):
        return self._list_rule
    @list_rule.setter
    def list_rule(self, rule):  # type: (ListRule) -> None
        self._list_rule = rule


    def convert(self, list_or_var):
        mylist = list_or_var
        if not isinstance(list_or_var, list):
            mylist = [list_or_var]






        apply_list_rule = {
            ListRule.keep_list: lambda v: v,
            ListRule.first_value: lambda v: v[0],
            ListRule.reduce_value: lambda v: reduce(self.list_reducer_func, v)
        }
        apply_one_element_list_rule = {
            OneElementListRule.follow_list_rule: lambda v: apply_list_rule[self.list_rule](v),
            OneElementListRule.first_value: lambda v: v[0],
        }
        apply_empty_list_rule = {
            EmptyListRule.none_value: None,
            EmptyListRule.bad_value: self.bad_value,
            EmptyListRule.keep_empty_list: [],
        }
        apply_bad_or_none_in_list_rule = {
            BadOrNoneInListRule.remove: lambda v: filter(lambda x: x is not None and x is not self.bad_value, v),
            BadOrNoneInListRule.none_value: lambda v: map(lambda x: None if x == self.bad_value else x, v),
            BadOrNoneInListRule.bad_value: lambda v: map(lambda x: self.bad_value if x is None else x, v),
        }

        mylist = apply_bad_or_none_in_list_rule[self.bad_or_none_in_list_rule](mylist)

        if len(mylist) <= 0:
            mylist = apply_empty_list_rule[self.empty_list_rule]
        elif len(mylist) == 1:
            mylist = apply_one_element_list_rule[self.one_element_list_rule](mylist)
        else:
            mylist = apply_list_rule[self.list_rule](mylist)


        return mylist
