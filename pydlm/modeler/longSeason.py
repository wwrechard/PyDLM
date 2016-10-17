"""
===========================================================================

The code for long seasonality components

===========================================================================

This code implements the long seasonality component as a sub-class of dynamic.
The difference between the long seasonality is that
1) The seasonality component use each date as a unit and change in a given
periodicy. For example, 1, 2, 3, 4, 1, 2, 3, 4.
2) However, the long seasonality is capable to group a couple of days as the
basic unit and change in a periodicy. For example, 1, 1, 1, 2, 2, 2, 3, 3, 3,
4, 4, 4.
The usecase for long seasonality is to model longer seasonality with the
short-term seasonality. For example, the short-term seansonality can be
used to model the day of a weak patten and the long seasonality can be used
to model the week of a month patten in the same model.
Different from the dynamic component, the features in the autoReg is generated
from the data, and updated according to the data. All other features are
similar to @dynamic.

"""

from .dynamic import dynamic


class longSeason(dynamic):
    """ The longSeason class alows user to add a long seasonality component
    to the dlm. The difference between the long seasonality is that
    1) The seasonality component use each date as a unit and change in a given
    periodicity. For example, 1, 2, 3, 4, 1, 2, 3, 4.
    2) However, the long seasonality is capable to group couple of days as the
    basic unit and change in a periodicity. For example, 1, 1, 1, 2, 2, 2,
    3, 3, 3, 4, 4, 4.
    The usecase for long seasonality is to model longer seasonality with the
    short-term seasonality. For example, the short-term seansonality can be
    used to model the day of a weak patten and the long seasonality can be used
    to model the week of a month patten in the same model.
    This code implements the longSeason component as a sub-class of
    dynamic. Different from the dynamic component, the features in the
    autoReg is generated from the data, and updated according to the data.
    All other features are similar to @dynamic.

    Attributes:
        period: the periodicity, i.e., how many different states it has in
                one period
        stay: the length of a state last.
        discount factor: the discounting factor
        name: the name of the component

    """

    def __init__(self,
                 data=None,
                 period=4,
                 stay=7,
                 discount=0.99,
                 name='longSeason'):

        self.period = period
        self.stay = stay

        # create features
        features, self.currentState = self.createFeatureMatrix(period=period,
                                                               stay=stay,
                                                               n=len(data),
                                                               state=[0, 0])

        dynamic.__init__(self,
                         features=features,
                         discount=discount,
                         name=name)
        self.checkDataLength()

        # modify the type to be autoReg
        self.componentType = 'longSeason'

    def createFeatureMatrix(self, period, stay, n, state):
        """ Create the feature matrix based on the supplied data and the degree.

        Args:
            period: the periodicity of the component
            stay: the length of the base unit, i.e, how long before change to
                  change to the next state.
        """

        # initialize feature matrix
        currentState = state
        features = []
        count = 0
        while count < n:
            currentState[1] = (currentState[1] + 1) % stay
            if currentState == 0:
                currentState[0] = (currentState[0] + 1) % period
            new_feature = [0] * period
            new_feature[currentState[0]] = 1
            features.append(new_feature)
            count += 1

        return features, currentState

    # the degree cannot be longer than data
    def checkDataLength(self):
        """ Check whether the degree is less than the time series length

        """
        if self.d >= self.n:
            raise NameError('The degree cannot be longer than the data series')

    # override
    def appendNewData(self, newData):
        """ Append new data to the existing features. Overriding the same method in
        @dynamic

        Args:
            newData: a list of new data

        """
        # create the new features
        newFeatures = self.createFeatureMatrix(period=self.period,
                                               stay=self.stay,
                                               n=len(newData),
                                               state=self.currentState)
        self.features.extend(newFeatures)
        self.n = len(self.features)

    # override
    def popout(self, date):
        """ Pop out the data of a specific date and rewrite the correct feature matrix.

        Args:
            date: the index of which to be deleted.

        """
        # Since the seasonality is a fixed patten,
        # no matter what date is popped out
        # we just need to remove the last date,
        # otherwise the feature patten will be
        # changed.

        # if you want to delete a date and change
        # the underlying patten, i.e., shorten
        # the periodicity of the period that date
        # is presented, you should use ignore
        # instead
        print('Popout the date will change the whole' +
              ' seasonality patten on all the' +
              'future days. If you want to keep the' +
              ' seasonality patten on the future' +
              'days unchanged. Please use ignore instead')

        self.features.pop()
        self.n -= 1

        # push currentState back by 1 day. Need to take care of all
        # corner cases.
        if self.currentState[1] == 0:
            self.currentState[1] = self.stay - 1
            if self.currentState[0] == 0:
                self.currentState[0] = self.period - 1
            else:
                self.currentState[0] -= 1
        else:
            self.currentState[1] -= 1
