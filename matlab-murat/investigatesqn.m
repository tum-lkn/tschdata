
len=length(freq_dumbinthop(:,1));

motessqndumbinthop=zeros(13,len);
maxsqn=ones(13,1);

for j=1:len
	motessqndumbinthop(hopaddr_dumbinthop(j,1),maxsqn(hopaddr_dumbinthop(j,1)))=sqn_dumbinthop(j); 
    %motes(hopaddr_dumbinthop(j,1),sqn_dumbinthop(j))=1; 
    maxsqn(hopaddr_dumbinthop(j,1))=maxsqn(hopaddr_dumbinthop(j,1))+1;
end
jump=zeros(13,1);
for j=2:len
    for i=1:13
        if motessqndumbinthop(i,j)<motessqndumbinthop(i,j-1)-50 && jump(i)==0; 
            jump(i)=motessqndumbinthop(i,j-1);
        elseif (motessqndumbinthop(i,j)+jump(i))< motessqndumbinthop(i,j-1)-50
            jump(i)=motessqndumbinthop(i,j-1);
        end
        if jump(i)~=0 && motessqndumbinthop(i,j)~=0
            motessqndumbinthop(i,j)=motessqndumbinthop(i,j)+jump(i);
        end
    end
end