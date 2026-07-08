:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

Inside nikon::NXHistory
=======================

..  code-block:: XML
    :caption: nikon::NXHistory sample

     <filter id="nikon::NXHistory">
        <active>true</active>
        <parameters>
            <historystep>
                <version>20</version>
                <feather>0</feather>
                <featherEnabled>false</featherEnabled>
                <baseFill>0</baseFill>
                <baseFillEnabled>true</baseFillEnabled>
                <paintToolsEnabled>true</paintToolsEnabled>
                <mixerEnabled>true</mixerEnabled>
                <adjustmentData>
                    <data id="NkOneStepAdjustment">true</data>
                </adjustmentData>
                <filter id="nik::AdaptivePaste">
                    <active>false</active>
                    <parameters>
                        <integer name="Version">1</integer>
                        ...
                    </parameters>
                </filter>
            </historystep>
            ...
            <historystep>
                <version>20</version>
                <feather>0</feather>
                <featherEnabled>false</featherEnabled>
                <baseFill>0</baseFill>
                <baseFillEnabled>true</baseFillEnabled>
                <paintToolsEnabled>true</paintToolsEnabled>
                <mixerEnabled>true</mixerEnabled>
                <adjustmentData>
                    <data id="NkOneStepAdjustment">true</data>
                </adjustmentData>
                <filter id="nik::Crop">
                    <active>true</active>
                    <parameters>
                        <integer name="version">1</integer>
                        <point name="cropStart" x="991" y="546"/>
                        <point name="cropEnd" x="5150" y="3180"/>
                        ...
                    </parameters>
                </filter>
            </historystep>
        </parameters>
    </filter>
