# plsql_queries.py

# Запрос для создания нового клиента
CREATE_CLIENT_QUERY = '''
declare
A           CLOB;
B           CLOB;
pserrdesc   varchar2(1000);
TEXT CLOB:= '
<MsgClientAddRq>
    <RqUID>{guid}</RqUID>
    <PersonForm>
        <PersonName>
            <NAMF>{NAMF}</NAMF>
            <NAMI>{NAMI}</NAMI>
            <NAMO>{NAMO}</NAMO>
        </PersonName>
        <PersonCommonInfo>
            <TSEX>мужской</TSEX>
            <BITH>{BITH}</BITH>
            <CINN>{CINN}</CINN>
            <TAGO>1</TAGO>
            <CNTR internal_id="643"/>
            <LBIR>Москва</LBIR>
            <WORK>ПСИТ PYTHON {computer_name}</WORK>
        </PersonCommonInfo>
        <IdentityPaper out_of_date="false" internal_id="0" deleted="false">
            <DCTP internal_id="1"/>
            <PNUM>{PNUM}</PNUM>
            <PSER>{PSER}</PSER>
            <PORG>ОВД Пресненского района 55</PORG>
            <DEPC>133-456</DEPC>
            <PDAT>2016-08-13</PDAT>
            <CNTR internal_id="643"></CNTR>
            <PDEX>2031-08-13</PDEX>
        </IdentityPaper>
        <PersonAddress>
            <PersonAddressType internal_id="1"></PersonAddressType>
            <AddressParams>
                <CNTR internal_id="643"></CNTR>
                <INDX>123456</INDX>
                <SITY>Москва</SITY>
                <TSIT>город</TSIT>
                <PNNM>Москва</PNNM>
                <STNM>Живописная</STNM>
                <STTP>улица</STTP>
                <HOUS>8</HOUS>
                <BLDN>1</BLDN>
                <COMP>2</COMP>
                <APRT>12</APRT>
            </AddressParams>
        </PersonAddress>
        <ContactInfo>
            <ContactType internal_id="21805"></ContactType>
            <TVAL>+9(905){TVAL}</TVAL>
            <TCOM>Комментарий не звонить</TCOM>
        </ContactInfo>
    </PersonForm>
</MsgClientAddRq>
';
begin
    B:=RRAM_HANDLER.UniMessHandler(TEXT,'DBO3CARDR',to_char(null),null,null,1, pserrdesc);
end;
'''

# Запрос для создания нового договора
CREATE_AGREEMENT_QUERY = '''
declare
B           CLOB;
pserrdesc   varchar2(1000);
TEXT CLOB:= '
<MsgAgreeAddRq actual_at_once="true">
    <RqUID>{guid}</RqUID>
    <ClientId>{last_clid}</ClientId>
    <AgreeRequest>
        <AgreeType internal_id="{AgreeType}"></AgreeType>
        <AgreeSum>100</AgreeSum>
        <AgreeCardInfo>
            <NotInstantCard>
                <MainParameters>
                    <GroupCardId internal_id="{id_group_card}"></GroupCardId>
                </MainParameters>
            </NotInstantCard>
        </AgreeCardInfo>
    </AgreeRequest>
</MsgAgreeAddRq>
';
begin
    B:=RRAM_HANDLER.UniMessHandler(TEXT,'DBO3CARDR',to_char(null),null,null,1, pserrdesc);
end;
'''
