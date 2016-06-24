


class TSCH_hopping:
    def __init__(self, filename):
        print('Creating a TSCH frame for %s' % filename)
        self.schedule = self.load_schedule(filename)

    def load_schedule(self,file):
        print("Test "+file)


if __name__ == '__main__':
    for i in range(1, 2):
        filename= "../../WHData/Data/triagnosys/%d.log" % i
        a = TSCH_hopping(filename)