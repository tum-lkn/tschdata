duppacks=zeros(40,1);
for l=1:630
countmult=0;
count=0;
for j=(l)*10:(l+1)*10
    for i=1:13
        if motes(i,j)>1
            count=count+1;
            countmult=countmult+motes(i,j)-1;
        elseif motes(i,j)==1
            count=count+1;
        end    
    end
end
duppacks(l)=countmult/count;
end

plot(10:10:6300,duppacks);