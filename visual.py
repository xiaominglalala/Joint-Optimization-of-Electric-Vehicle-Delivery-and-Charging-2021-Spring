import matplotlib.pyplot as plt
x = [1000, 2000, 3000, 4000, 5000]
ig1=[ 7035.888195498032,6659.570659090933,6222.735246196005,5983.851083055672, 5775.854454710388]
ig2=[5903.39427281552,4944.25570748834,4891.63471805021,4891.63471805021,4891.63471805021]
ig3=[ 5883.338010239799,5377.848213487361,5377.848213487361,5377.848213487361,5377.848213487361]
ig4=[ 6494.383074503295, 5797.35670913032,5581.153343042562,5581.153343042562,5581.153343042562]
ig5=[ 6329.316116851232, 5423.782284871777,5348.856004415229,5309.919074006913,5256.843428315987]


plt.plot(x, ig1, 's-', color = 'r', label = "Improved")
plt.plot(x, ig2, 's-', color = 'r')
plt.plot(x, ig3, 's-', color = 'r')
plt.plot(x, ig4, 's-', color = 'r')
plt.plot(x, ig5, 's-', color = 'r')

g1 = [7262.52021176701, 7019.367182059717, 6107.432427766328,  6711.19792934644, 7173.157001291291]
g2 = [6295.463038813395,6391.595474275497,6462.363293815385, 6665.061466456736,6453.368118258941]
g3 = [6901.185135424811 ,6417.895688543355 ,6134.143950728724 , 6144.146228909072 ,5952.017866896439 ]
g4 = [ 6069.019001837303, 6149.664744950059, 6719.734049850241,6212.167863516044 , 6267.975752661481]
g5 = [ 6944.118864984991,6859.1705148049505 , 6370.111988056358, 6016.592518321808,6416.220831868831 ]


plt.plot(x, g1, 'o-', color = 'g', label = "Original")
plt.plot(x, g2, 'o-', color = 'g')
plt.plot(x, g3, 'o-', color = 'g')
plt.plot(x, g4, 'o-', color = 'g')
plt.plot(x, g5, 'o-', color = 'g')

plt.xlabel("Iteration times")
plt.ylabel("Cost")
plt.legend(loc = "best")
plt.show()

ig_mean = []
g_mean = []
total_width, n = 0.8, 2
width = total_width/n
for i in range(5):
    g_mean.append((g1[i]+g2[i]+g3[i]+g4[i]+g5[i])/5)
    ig_mean.append((ig1[i]+ig2[i]+ig3[i]+ig4[i]+ig5[i])/5)
name_list = [1000, 2000, 3000, 4000, 5000]
a = list(range(len(name_list)))
plt.bar(a, g_mean, width = width, label = 'Original', tick_label = name_list, fc = 'g')

for i in range(len(a)):
    a[i] = a[i] + width
plt.bar(a, ig_mean, width = width, label = 'Improved', fc = 'r')
plt.xlabel("Iteration times")
plt.ylabel("Cost")
plt.legend()
plt.show()

print(ig_mean)
print(g_mean)
for i in range(5):
    print(str(((g_mean[i]-ig_mean[i])/g_mean[i])*100) + "%")